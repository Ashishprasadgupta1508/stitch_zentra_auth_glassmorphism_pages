import asyncio
import json
import logging
import os
import threading
from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

try:
    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import auth as firebase_auth
    firebase_available = True
except Exception:
    firebase_available = False

logger = logging.getLogger(__name__)

from .models import DailyTask, Lecture, Note, Test, UserProgress
from .services import AIService, create_test_for_lecture, process_note_in_background, unlock_next_lecture, unlock_next_task


MAX_UPLOAD_SIZE = 20 * 1024 * 1024
User = get_user_model()


def serialize_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'topic': task.topic.name if task.topic else '',
        'topic_id': task.topic.id if task.topic else None,
        'estimated_time': float(task.study_time_hours),
        'study_time_hours': float(task.study_time_hours),
        'status': task.status,
        'completed': task.status == 'completed',
        'locked': task.status == 'locked',
    }


def serialize_topic(topic):
    return {
        'id': topic.id,
        'name': topic.name,
        'title': topic.name,
        'summary': topic.summary,
        'difficulty': topic.difficulty_level,
        'difficulty_level': topic.difficulty_level,
        'estimated_time': float(topic.study_time_hours),
        'study_time_hours': float(topic.study_time_hours),
    }


def get_course_completion_payload(user):
    lectures = Lecture.objects.filter(note__user=user)
    tests = Test.objects.filter(note__user=user)
    total_lectures = lectures.count()
    completed_lectures = lectures.filter(status='completed').count()
    completed_tests = tests.filter(completed=True).count()
    completed_scores = list(tests.filter(completed=True).values_list('score', flat=True))
    average_score = round(sum(completed_scores) / len(completed_scores)) if completed_scores else 0
    completion_percent = round((completed_lectures / total_lectures) * 100) if total_lectures else 0
    study_time = sum(float(task.study_time_hours) for task in DailyTask.objects.filter(note__user=user, status='completed'))
    weak_topics = list(
        tests.filter(completed=True, score__lt=60)
        .values_list('lecture__topic__name', flat=True)
    )
    strong_topics = list(
        tests.filter(completed=True, score__gte=60)
        .values_list('lecture__topic__name', flat=True)
    )
    course_completed = bool(
        total_lectures
        and completed_lectures == total_lectures
        and completed_tests >= total_lectures
    )
    return {
        'course_completed': course_completed,
        'final_report': {
            'overall_score': average_score,
            'completion_percent': completion_percent,
            'average_accuracy': average_score,
            'study_time': study_time,
            'recommendation': 'Review weak topics before moving into new material.' if any(weak_topics) else 'Great work. Keep revising to retain your strongest topics.',
            'weak_topics': [topic for topic in weak_topics if topic],
            'strong_topics': [topic for topic in strong_topics if topic],
        },
    }


def serialize_note_dashboard(note):
    topics = list(note.topics.all())
    lectures = list(note.lectures.all())
    return {
        'id': note.id,
        'note_id': note.id,
        'subject': note.title,
        'title': note.title,
        'summary': note.summary,
        'difficulty': note.difficulty_level,
        'difficulty_level': note.difficulty_level,
        'estimated_study_time': float(note.estimated_study_time_hours),
        'estimated_study_time_hours': float(note.estimated_study_time_hours),
        'learning_plan': note.learning_plan,
        'modules': [
            {
                'id': lecture.id,
                'title': lecture.title,
                'topic_id': lecture.topic.id if lecture.topic else None,
                'status': lecture.status,
                'locked': lecture.status == 'locked',
            }
            for lecture in lectures
        ],
        'topics': [serialize_topic(topic) for topic in topics],
        'processing_status': note.processing_status,
    }


def initialize_firebase_admin():
    if not firebase_available:
        return False
    if firebase_admin.apps:
        return True
    try:
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT', '').strip()
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '').strip()
        if service_account_json:
            firebase_admin.initialize_app(credentials.Certificate(json.loads(service_account_json)))
        elif credentials_path:
            firebase_admin.initialize_app(credentials.Certificate(credentials_path))
        else:
            firebase_admin.initialize_app()
        return True
    except Exception:
        logger.exception('Firebase Admin SDK initialization failed')
        return False


def get_or_create_user_from_firebase(decoded: dict):
    uid = (decoded.get('uid') or '').strip()
    if not uid:
        return None

    email = decoded.get('email') or decoded.get('firebase', {}).get('email') or ''
    name = decoded.get('name') or decoded.get('displayName') or email or uid
    email_verified = bool(decoded.get('email_verified', False))
    field_names = {field.name for field in User._meta.fields}
    lookup = {'uid': uid} if 'uid' in field_names else {'username': f'fb_{uid}'}
    defaults = {}
    if 'username' in field_names:
        defaults['username'] = f'fb_{uid}'
    if 'email' in field_names:
        defaults['email'] = email or ''
    if 'name' in field_names:
        defaults['name'] = name or ''
    if 'first_name' in field_names:
        defaults['first_name'] = str(name).split(' ', 1)[0][:150]
    if 'email_verified' in field_names:
        defaults['email_verified'] = email_verified
    if 'is_active' in field_names:
        defaults['is_active'] = True

    user, created = User.objects.get_or_create(**lookup, defaults=defaults)
    update_fields = []
    if 'email' in field_names and email and user.email != email:
        user.email = email
        update_fields.append('email')
    if 'name' in field_names and name and getattr(user, 'name', '') != name:
        user.name = name
        update_fields.append('name')
    first_name = str(name).split(' ', 1)[0][:150]
    if 'first_name' in field_names and first_name and getattr(user, 'first_name', '') != first_name:
        user.first_name = first_name
        update_fields.append('first_name')
    if 'email_verified' in field_names and getattr(user, 'email_verified', None) != email_verified:
        user.email_verified = email_verified
        update_fields.append('email_verified')
    if update_fields:
        user.save(update_fields=update_fields)
    return user


def get_active_user(request):
    # Prefer Django session authentication when available
    try:
        if hasattr(request, 'user') and request.user.is_authenticated:
            return request.user
    except Exception:
        logger.exception('Error checking request.user')

    # Support Firebase ID token in Authorization: Bearer <token>
    auth_header = request.META.get('HTTP_AUTHORIZATION') or request.META.get('Authorization')
    if auth_header and auth_header.lower().startswith('bearer '):
        token = auth_header.split(' ', 1)[1].strip()
        if token:
            if initialize_firebase_admin():
                try:
                    decoded = firebase_auth.verify_id_token(token)
                    user = get_or_create_user_from_firebase(decoded)
                    if user:
                        return user
                except Exception:
                    logger.exception('Failed to verify Firebase token')
            else:
                logger.debug('Firebase admin not available; cannot verify token')

    # Fallback for deployments where Firebase Admin is not configured yet but the
    # client is already authenticated with Firebase. This allows the dashboard to
    # continue functioning while still creating a user record for the signed-in UID.
    firebase_uid = (
        request.META.get('HTTP_X_FIREBASE_UID')
        or request.META.get('HTTP_X_UID')
        or request.META.get('HTTP_X_USER_UID')
        or request.META.get('X_FIREBASE_UID')
        or ''
    ).strip()
    if firebase_uid:
        email = (
            request.META.get('HTTP_X_FIREBASE_EMAIL')
            or request.META.get('HTTP_X_USER_EMAIL')
            or request.META.get('X_FIREBASE_EMAIL')
            or ''
        ).strip()
        name = (
            request.META.get('HTTP_X_FIREBASE_NAME')
            or request.META.get('HTTP_X_USER_NAME')
            or request.META.get('X_FIREBASE_NAME')
            or ''
        ).strip()
        user = get_or_create_user_from_firebase({'uid': firebase_uid, 'email': email, 'name': name})
        if user:
            return user

    # Fallback for local development: provide demo user in DEBUG mode
    if settings.DEBUG:
        user, _ = User.objects.get_or_create(username='demo_student', defaults={'is_active': True})
        return user
    return None


@csrf_exempt
@require_POST
def upload_note(request):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Authentication is required.'}, status=401)

    file_obj: Optional[UploadedFile] = request.FILES.get('file')
    title = (request.POST.get('title') or 'Uploaded Notes').strip()
    if not file_obj:
        return JsonResponse({'success': False, 'error': 'No file provided.'}, status=400)
    if file_obj.size > MAX_UPLOAD_SIZE:
        return JsonResponse({'success': False, 'error': 'File must be smaller than 20MB.'}, status=400)
    if not file_obj.name.lower().endswith('.pdf'):
        return JsonResponse({'success': False, 'error': 'Only PDF uploads are supported.'}, status=400)

    note = Note.objects.create(user=user, title=title, file=file_obj)
    
    # Extract PDF text synchronously (fast operation) so AI can answer questions immediately
    try:
        ai_service = AIService()
        note.original_text = ai_service.extract_text_from_pdf(note.file.path)
        note.processing_status = 'processing' if note.original_text else 'failed'
        note.completed = False
        note.save(update_fields=['original_text', 'processing_status', 'completed'])
        logger.debug(f'Extracted {len(note.original_text)} characters from PDF for note {note.id}')
    except Exception as e:
        logger.exception(f'Failed to extract PDF text for note {note.id}: {str(e)}')
        note.processing_status = 'failed'
        note.completed = False
        note.save(update_fields=['processing_status', 'completed'])
    
    # Background processing for embeddings, analysis, lectures (slower operations)
    threading.Thread(target=lambda: asyncio.run(process_note_in_background(note)), daemon=True).start()
    return JsonResponse({'success': True, 'note_id': note.id, 'status': 'ready' if note.original_text else 'processing'})


@require_GET
def note_list(request):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'notes': []})
    notes = Note.objects.filter(user=user).values('id', 'title', 'summary', 'difficulty_level', 'estimated_study_time_hours', 'processing_status', 'created_at')
    return JsonResponse({'notes': list(notes)})


@require_GET
def note_detail(request, note_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    note = get_object_or_404(Note, id=note_id, user=user)
    unlock_next_task(note)
    unlock_next_lecture(note)
    lecture_payloads = []
    for lecture in note.lectures.all():
        lecture_test = getattr(lecture, 'test', None)
        lecture_payloads.append({
            'id': lecture.id,
            'title': lecture.title,
            'content': lecture.content,
            'status': lecture.status,
            'topic_id': lecture.topic.id if lecture.topic else None,
            'sequence_order': lecture.sequence_order,
            'test': {
                'id': lecture_test.id,
                'questions': lecture_test.questions,
                'completed': lecture_test.completed,
                'score': lecture_test.score,
            } if lecture_test else None,
        })

    return JsonResponse({
        'id': note.id,
        'note_id': note.id,
        'subject': note.title,
        'title': note.title,
        'summary': note.summary,
        'difficulty': note.difficulty_level,
        'difficulty_level': note.difficulty_level,
        'estimated_study_time': float(note.estimated_study_time_hours),
        'estimated_study_time_hours': float(note.estimated_study_time_hours),
        'learning_plan': note.learning_plan,
        'processing_status': note.processing_status,
        'topics': list(note.topics.values('id', 'name', 'summary', 'difficulty_level', 'study_time_hours', 'order')),
        'modules': [
            {
                'id': lecture['id'],
                'title': lecture['title'],
                'topic_id': lecture.get('topic_id'),
                'status': lecture['status'],
                'locked': lecture['status'] == 'locked',
            }
            for lecture in lecture_payloads
        ],
        'tasks': list(note.daily_tasks.values('id', 'title', 'task_type', 'study_time_hours', 'status', 'sequence_order')),
        'lectures': lecture_payloads,
    })


@require_GET
def tasks_for_note(request, note_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    note = get_object_or_404(Note, id=note_id, user=user)
    return JsonResponse({'note_id': note.id, 'tasks': [serialize_task(task) for task in note.daily_tasks.all()]})


@require_GET
def lecture_for_topic(request, topic_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    lecture = get_object_or_404(Lecture, topic_id=topic_id, note__user=user)
    if lecture.status == 'locked':
        return JsonResponse({'error': 'Lecture is locked.', 'locked': True}, status=403)
    return JsonResponse({
        'id': lecture.id,
        'topic_id': topic_id,
        'title': lecture.title,
        'explanation': lecture.content,
        'examples': [],
        'key_points': [],
        'status': lecture.status,
    })


@require_GET
def test_for_topic(request, topic_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    lecture = get_object_or_404(Lecture, topic_id=topic_id, note__user=user)
    if lecture.status == 'locked':
        return JsonResponse({'error': 'Test is locked.', 'locked': True}, status=403)
    test = create_test_for_lecture(lecture)
    return JsonResponse({
        'id': test.id,
        'topic_id': topic_id,
        'questions': test.questions,
        'completed': test.completed,
        'score': test.score,
    })


@csrf_exempt
@require_POST
def submit_test_for_topic(request, topic_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    lecture = get_object_or_404(Lecture, topic_id=topic_id, note__user=user)
    test = create_test_for_lecture(lecture)
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        payload = {}
    answers = payload.get('answers') or {}
    score = 0
    correct = 0
    total = len(test.questions or [])
    was_test_completed = test.completed
    was_lecture_completed = lecture.status == 'completed'
    if answers and test.questions:
        for index, question in enumerate(test.questions):
            expected = str(question.get('answer', '')).strip().lower()
            provided = str(answers.get(str(index), answers.get(index, ''))).strip().lower()
            if expected and provided == expected:
                correct += 1
        score = round((correct / total) * 100) if total else 0
    test.score = score
    test.completed = True
    test.save(update_fields=['score', 'completed'])
    lecture.status = 'completed'
    lecture.save(update_fields=['status'])
    progress, _ = UserProgress.objects.get_or_create(user=user, note=lecture.note)
    progress_updates = []
    if not was_test_completed:
        progress.completed_tests += 1
        progress_updates.append('completed_tests')
    if not was_lecture_completed:
        progress.completed_lectures += 1
        progress_updates.append('completed_lectures')
    if progress_updates:
        progress.save(update_fields=progress_updates)
    passed = True
    next_task_unlocked = False
    next_lecture_unlocked = False
    task = DailyTask.objects.filter(note=lecture.note, topic=lecture.topic).first()
    if task and task.status != 'completed':
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save(update_fields=['status', 'completed_at'])
        progress.completed_tasks += 1
        progress.save(update_fields=['completed_tasks'])
    unlock_next_task(lecture.note)
    unlock_next_lecture(lecture.note)
    next_task_unlocked = True
    next_lecture_unlocked = True
    weak_topics = [] if score >= 60 else [lecture.topic.name if lecture.topic else lecture.title]
    strong_topics = [lecture.topic.name if lecture.topic else lecture.title] if score >= 60 else []
    completion_payload = get_course_completion_payload(user)
    return JsonResponse({
        'success': True,
        'score': score,
        'accuracy': score,
        'correct': correct,
        'wrong': max(total - correct, 0),
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'passed': passed,
        'next_task_unlocked': next_task_unlocked,
        'next_lecture_unlocked': next_lecture_unlocked,
        **completion_payload,
    })


@require_GET
def progress_summary(request):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    notes = Note.objects.filter(user=user).prefetch_related('topics', 'daily_tasks')
    total_topics = sum(note.topics.count() for note in notes)
    completed_topics = Lecture.objects.filter(note__user=user, status='completed').count()
    completed_tasks = DailyTask.objects.filter(note__user=user, status='completed').count()
    completed_tests = Test.objects.filter(note__user=user, completed=True).count()
    total_tasks = DailyTask.objects.filter(note__user=user).count()
    study_time = sum(float(task.study_time_hours) for task in DailyTask.objects.filter(note__user=user, status='completed'))
    completion = round((completed_topics / total_topics) * 100) if total_topics else 0
    scores = list(Test.objects.filter(note__user=user, completed=True).values_list('score', flat=True))
    average_score = round(sum(scores) / len(scores)) if scores else 0
    weak_topics = list(
        Lecture.objects.filter(note__user=user, test__completed=True, test__score__lt=60)
        .values_list('topic__name', flat=True)
    )
    strong_topics = list(
        Lecture.objects.filter(note__user=user, test__completed=True, test__score__gte=60)
        .values_list('topic__name', flat=True)
    )
    current_lecture = Lecture.objects.filter(note__user=user).exclude(status='completed').order_by('note__created_at', 'sequence_order', 'id').first()
    return JsonResponse({
        'overall_progress': completion,
        'completed_topics': completed_topics,
        'completed_lectures': completed_topics,
        'remaining_topics': max(total_topics - completed_topics, 0),
        'current_streak': 0,
        'study_time': study_time,
        'weak_topics': [topic for topic in weak_topics if topic],
        'strong_topics': [topic for topic in strong_topics if topic],
        'completion_percent': completion,
        'completed_tasks': completed_tasks,
        'completed_tests': completed_tests,
        'average_score': average_score,
        'accuracy': average_score,
        'average_accuracy': average_score,
        'current_module': current_lecture.title if current_lecture else '',
        'current_topic': current_lecture.topic.name if current_lecture and current_lecture.topic else '',
        'total_tasks': total_tasks,
    })


@csrf_exempt
@require_POST
def start_task(request, task_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    task = get_object_or_404(DailyTask, id=task_id, note__user=user)
    if task.status == 'locked':
        return JsonResponse({'error': 'Task is locked.', 'locked': True, 'task': serialize_task(task)}, status=403)
    if task.status == 'unlocked':
        task.status = 'in_progress'
        task.save(update_fields=['status'])
    lecture = Lecture.objects.filter(note=task.note, topic=task.topic).first()
    if lecture and lecture.status == 'locked':
        lecture.status = 'unlocked'
        lecture.save(update_fields=['status'])
    return JsonResponse({
        'success': True,
        'task': serialize_task(task),
        'topic_id': task.topic.id if task.topic else None,
        'lecture_id': lecture.id if lecture else None,
        'lecture': {
            'id': lecture.id,
            'title': lecture.title,
            'status': lecture.status,
        } if lecture else None,
    })


@csrf_exempt
@require_POST
def complete_task(request, task_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    task = get_object_or_404(DailyTask, id=task_id, note__user=user)
    if task.status == 'completed':
        return JsonResponse({'success': True, 'message': 'Task already completed.', 'task': serialize_task(task), 'next_task_unlocked': False})
    task.status = 'completed'
    task.completed_at = timezone.now()
    task.save(update_fields=['status', 'completed_at'])
    next_task_unlocked = unlock_next_task(task.note)
    progress, _ = UserProgress.objects.get_or_create(user=user, note=task.note)
    progress.completed_tasks += 1
    progress.save(update_fields=['completed_tasks'])
    return JsonResponse({'success': True, 'task': serialize_task(task), 'next_task_unlocked': next_task_unlocked})


@require_GET
def lecture_detail(request, lecture_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    lecture = get_object_or_404(Lecture, id=lecture_id, note__user=user)
    if not hasattr(lecture, 'test'):
        test = create_test_for_lecture(lecture)
    else:
        test = lecture.test
    return JsonResponse({
        'id': lecture.id,
        'title': lecture.title,
        'content': lecture.content,
        'status': lecture.status,
        'test': {
            'id': test.id,
            'questions': test.questions,
            'completed': test.completed,
            'score': test.score,
        },
    })


@csrf_exempt
@require_POST
def complete_lecture(request, lecture_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    lecture = get_object_or_404(Lecture, id=lecture_id, note__user=user)
    test = create_test_for_lecture(lecture)
    if lecture.status == 'completed':
        return JsonResponse({'success': True, 'message': 'Lecture already completed.', 'lecture': {'id': lecture.id, 'status': lecture.status}, 'test': {'id': test.id, 'questions': test.questions}})
    lecture.status = 'completed'
    lecture.save(update_fields=['status'])
    progress, _ = UserProgress.objects.get_or_create(user=user, note=lecture.note)
    progress.completed_lectures += 1
    progress.save(update_fields=['completed_lectures'])
    return JsonResponse({'success': True, 'lecture': {'id': lecture.id, 'status': lecture.status}, 'test': {'id': test.id, 'questions': test.questions}})


@csrf_exempt
@require_POST
def submit_test(request, test_id):
    user = get_active_user(request)
    if not user:
        return JsonResponse({'error': 'Authentication is required.'}, status=401)
    test = get_object_or_404(Test, id=test_id, note__user=user)
    payload = json.loads(request.body.decode('utf-8') or '{}')
    answers = payload.get('answers') or {}
    score = int(payload.get('score', 0))
    correct = 0
    total = len(test.questions or [])
    was_test_completed = test.completed
    if answers and test.questions:
        for index, question in enumerate(test.questions):
            expected = str(question.get('answer', '')).strip().lower()
            provided = str(answers.get(str(index), answers.get(index, ''))).strip().lower()
            if expected and provided == expected:
                correct += 1
        score = round((correct / total) * 100) if total else 0
    test.score = score
    test.completed = True
    test.save(update_fields=['score', 'completed'])
    progress, _ = UserProgress.objects.get_or_create(user=user, note=test.note)
    if not was_test_completed:
        progress.completed_tests += 1
        progress.save(update_fields=['completed_tests'])
    passed = True
    next_task_unlocked = False
    next_lecture_unlocked = False
    task = DailyTask.objects.filter(note=test.note, topic=test.lecture.topic).first()
    if task and task.status != 'completed':
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save(update_fields=['status', 'completed_at'])
        progress.completed_tasks += 1
        progress.save(update_fields=['completed_tasks'])
    unlock_next_task(test.note)
    unlock_next_lecture(test.note)
    next_task_unlocked = True
    next_lecture_unlocked = True
    weak_topics = [] if passed else [test.lecture.topic.name if test.lecture.topic else test.lecture.title]
    strong_topics = [test.lecture.topic.name if test.lecture.topic else test.lecture.title] if passed else []
    completion_payload = get_course_completion_payload(user)
    return JsonResponse({
        'success': True,
        'test': {'id': test.id, 'score': test.score, 'completed': test.completed},
        'score': score,
        'accuracy': score,
        'correct': correct,
        'wrong': max(total - correct, 0),
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'passed': passed,
        'next_task_unlocked': next_task_unlocked,
        'next_lecture_unlocked': next_lecture_unlocked,
        **completion_payload,
    })


@csrf_exempt
@require_POST
def chat_with_ai(request):
    """
    Chat endpoint for AI Insights.
    Accepts: { message } or { note_id, messages: [{ role, message }, ...] }
    Returns: { success, answer } or error response.
    CSRF exempt for cross-origin development. Will need CSRF token or session auth in production.
    """
    try:
        user = get_active_user(request)
        if not user:
            logger.debug('chat_with_ai: No authenticated user found')
            return JsonResponse({'success': False, 'error': 'Authentication is required.'}, status=401)

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError as e:
            logger.debug('chat_with_ai: Invalid JSON payload: %s', str(e))
            return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)

        note_id = payload.get('note_id')
        messages = payload.get('messages') or []
        message = (payload.get('message') or '').strip()
        if message and not messages:
            messages = [{'role': 'user', 'message': message}]
        if not messages or not isinstance(messages, list):
            logger.debug('chat_with_ai: Missing or invalid messages array')
            return JsonResponse({'success': False, 'error': 'message is required.'}, status=400)

        # Validate at least one user message
        user_messages = [m for m in messages if m.get('role') == 'user' and m.get('message')]
        if not user_messages:
            logger.debug('chat_with_ai: No user messages in array')
            return JsonResponse({'success': False, 'error': 'At least one user message is required.'}, status=400)

        # Ensure the note exists and belongs to the user
        note = None
        note_text = ''
        topics = []
        if note_id:
            try:
                note = Note.objects.get(id=note_id, user=user)
                logger.debug('chat_with_ai: Found note %d for user %s', note_id, user.username)
                note_text = note.original_text or ''
                topics = list(note.topics.values('name', 'summary', 'difficulty_level', 'study_time_hours'))
            except Note.DoesNotExist:
                logger.debug('chat_with_ai: Note %d not found for user %s', note_id, user.username)
                return JsonResponse({'success': False, 'error': 'Note not found or access denied.'}, status=404)
            except Exception as e:
                logger.exception('chat_with_ai: Error fetching note %s for user %s: %s', note_id, user.username, str(e))
                return JsonResponse({'success': False, 'error': 'Failed to retrieve note.'}, status=500)
        else:
            logger.debug('chat_with_ai: No note_id provided; user %s asking general question', user.username)

        # If note provided and embeddings are missing, create them now
        if note and not getattr(note, 'embeddings', None):
            try:
                logger.debug('chat_with_ai: Creating embeddings for note %d', note.id)
                ai_service = AIService()
                embeddings = ai_service.create_embeddings(note_text)
                note.embeddings = embeddings
                note.save(update_fields=['embeddings'])
                logger.debug('chat_with_ai: Embeddings created for note %d', note.id)
            except Exception as e:
                logger.exception('chat_with_ai: Failed to create embeddings for note %s: %s', note.id, str(e))
                # Log but don't fail; continue without embeddings

        # Call AI service to generate response
        answer = ''
        try:
            logger.debug('chat_with_ai: Calling AIService.chat with %d messages for user %s', len(messages), user.username)
            ai = AIService()
            answer = ai.chat(messages, note_text, topics)
            logger.debug('chat_with_ai: Got answer (first 150 chars): %s', answer[:150] if answer else '(empty)')
        except Exception as e:
            logger.exception('chat_with_ai: AIService.chat failed for user %s, note_id %s: %s', user.username, note_id, str(e))
            return JsonResponse({'success': False, 'error': 'AI service failed to generate a response.'}, status=500)

        return JsonResponse({'success': True, 'answer': answer})
    except Exception as e:
        logger.exception('chat_with_ai: Unexpected error: %s', str(e))
        return JsonResponse({'success': False, 'error': 'Internal server error.'}, status=500)

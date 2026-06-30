from django.contrib.auth import get_user_model
import json

from django.test import Client, TestCase

from .services import create_learning_flow
from .views import get_or_create_user_from_firebase
from .models import DailyTask, Lecture, Note, Test, Topic


class LearningFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='student', password='student123')

    def test_learning_flow_creates_sequential_tasks_and_lectures(self):
        note = Note.objects.create(
            user=self.user,
            title='Biology Basics',
            summary='Cells are the building blocks of life.',
            difficulty_level='medium',
            estimated_study_time_hours=2.5,
            processing_status='completed',
        )
        Topic.objects.create(note=note, name='Cell Structure', summary='Overview of cells', difficulty_level='easy', study_time_hours=1.0, order=1)
        Topic.objects.create(note=note, name='DNA Basics', summary='DNA fundamentals', difficulty_level='medium', study_time_hours=1.5, order=2)

        created = create_learning_flow(note)

        self.assertTrue(created['tasks'])
        self.assertTrue(created['lectures'])
        self.assertEqual(created['tasks'][0].status, 'unlocked')
        self.assertEqual(created['tasks'][1].status, 'locked')
        self.assertEqual(created['lectures'][0].status, 'unlocked')
        self.assertEqual(created['lectures'][1].status, 'locked')


class ApiPostCsrfTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = get_user_model().objects.create_user(username='student', password='student123')
        self.client.force_login(self.user)
        self.note = Note.objects.create(
            user=self.user,
            title='Physics Notes',
            summary='Motion and force.',
            processing_status='completed',
        )
        self.task = DailyTask.objects.create(
            note=self.note,
            title='Review motion',
            task_type='Study',
            study_time_hours=1,
            status='unlocked',
            sequence_order=1,
        )
        self.lecture = Lecture.objects.create(
            note=self.note,
            title='Motion lecture',
            content='Motion basics',
            status='unlocked',
            sequence_order=1,
        )
        self.test = Test.objects.create(lecture=self.lecture, note=self.note, questions=[], score=0)

    def test_complete_task_allows_static_dashboard_post_without_csrf_token(self):
        response = self.client.post(f'/api/tasks/{self.task.id}/complete/')

        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_submit_test_allows_static_dashboard_post_without_csrf_token(self):
        response = self.client.post(
            f'/api/tests/{self.test.id}/submit/',
            data=json.dumps({'score': 100}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.test.refresh_from_db()
        self.assertTrue(self.test.completed)
        self.assertEqual(self.test.score, 100)

    def test_chat_accepts_simple_message_payload(self):
        response = self.client.post(
            '/api/insights/chat/',
            data=json.dumps({'message': 'Hello'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('answer', response.json())


class TestProgressionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='student', password='student123')
        self.client.force_login(self.user)
        self.note = Note.objects.create(
            user=self.user,
            title='Math Notes',
            summary='Algebra and geometry.',
            processing_status='completed',
        )
        self.topic_one = Topic.objects.create(note=self.note, name='Algebra', order=1)
        self.topic_two = Topic.objects.create(note=self.note, name='Geometry', order=2)
        self.task_one = DailyTask.objects.create(
            note=self.note,
            topic=self.topic_one,
            title='Study Algebra',
            status='in_progress',
            sequence_order=1,
        )
        self.task_two = DailyTask.objects.create(
            note=self.note,
            topic=self.topic_two,
            title='Study Geometry',
            status='locked',
            sequence_order=2,
        )
        self.lecture_one = Lecture.objects.create(
            note=self.note,
            topic=self.topic_one,
            title='Lecture: Algebra',
            status='unlocked',
            sequence_order=1,
        )
        self.lecture_two = Lecture.objects.create(
            note=self.note,
            topic=self.topic_two,
            title='Lecture: Geometry',
            status='locked',
            sequence_order=2,
        )
        self.test_one = Test.objects.create(
            lecture=self.lecture_one,
            note=self.note,
            questions=[{'type': 'mcq', 'question': '2 + 2?', 'options': ['3', '4'], 'answer': '4'}],
            score=0,
        )

    def test_low_score_topic_test_still_unlocks_next_task_and_lecture(self):
        response = self.client.post(
            f'/api/test/{self.topic_one.id}/submit/',
            data=json.dumps({'answers': {'0': '3'}}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['score'], 0)
        self.assertTrue(data['passed'])
        self.assertTrue(data['next_task_unlocked'])
        self.assertTrue(data['next_lecture_unlocked'])

        self.task_one.refresh_from_db()
        self.task_two.refresh_from_db()
        self.lecture_one.refresh_from_db()
        self.lecture_two.refresh_from_db()
        self.assertEqual(self.task_one.status, 'completed')
        self.assertEqual(self.task_two.status, 'unlocked')
        self.assertEqual(self.lecture_one.status, 'completed')
        self.assertEqual(self.lecture_two.status, 'unlocked')

    def test_passing_topic_test_unlocks_next_task_and_lecture(self):
        response = self.client.post(
            f'/api/test/{self.topic_one.id}/submit/',
            data=json.dumps({'answers': {'0': '4'}}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['score'], 100)
        self.assertTrue(data['passed'])
        self.assertTrue(data['next_task_unlocked'])
        self.assertTrue(data['next_lecture_unlocked'])

        self.task_one.refresh_from_db()
        self.task_two.refresh_from_db()
        self.lecture_one.refresh_from_db()
        self.lecture_two.refresh_from_db()
        self.assertEqual(self.task_one.status, 'completed')
        self.assertEqual(self.task_two.status, 'unlocked')
        self.assertEqual(self.lecture_one.status, 'completed')
        self.assertEqual(self.lecture_two.status, 'unlocked')

    def test_loading_tasks_does_not_unlock_next_item(self):
        self.task_one.status = 'completed'
        self.task_one.save(update_fields=['status'])
        self.lecture_one.status = 'completed'
        self.lecture_one.save(update_fields=['status'])

        response = self.client.get(f'/api/tasks/{self.note.id}/')

        self.assertEqual(response.status_code, 200)
        self.task_two.refresh_from_db()
        self.lecture_two.refresh_from_db()
        self.assertEqual(self.task_two.status, 'locked')
        self.assertEqual(self.lecture_two.status, 'locked')

    def test_locked_lecture_does_not_open_just_because_previous_lecture_completed(self):
        self.lecture_one.status = 'completed'
        self.lecture_one.save(update_fields=['status'])

        response = self.client.get(f'/api/lecture/{self.topic_two.id}/')

        self.assertEqual(response.status_code, 403)
        self.lecture_two.refresh_from_db()
        self.assertEqual(self.lecture_two.status, 'locked')


class FirebaseUserTests(TestCase):
    def test_verified_firebase_payload_creates_and_updates_user(self):
        decoded = {
            'uid': 'abc123',
            'email': 'student@example.com',
            'name': 'Student Example',
        }

        user = get_or_create_user_from_firebase(decoded)

        self.assertEqual(user.username, 'fb_abc123')
        self.assertEqual(user.email, 'student@example.com')
        self.assertEqual(user.first_name, 'Student')

        updated = get_or_create_user_from_firebase({
            'uid': 'abc123',
            'email': 'new@example.com',
            'name': 'New Name',
        })

        self.assertEqual(updated.id, user.id)
        self.assertEqual(updated.email, 'new@example.com')
        self.assertEqual(updated.first_name, 'New')

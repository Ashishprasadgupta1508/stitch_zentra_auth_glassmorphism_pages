import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List
import hashlib
import logging

from django.conf import settings
from django.core.files.base import File
from django.utils import timezone
from pypdf import PdfReader

from .models import DailyTask, Lecture, Note, Test, Topic, UserProgress

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - environment fallback
    genai = None


class AIService:
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
        self.model_name = getattr(settings, 'GEMINI_MODEL', '') or os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.model = None
        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
            except Exception:
                self.model = None

    def _call_model(self, prompt: str, *, temperature: float = 0.2) -> str:
        if not self.model:
            return ''
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': temperature,
                    'top_p': 0.9,
                    'max_output_tokens': 1200,
                },
            )
            return getattr(response, 'text', '') or ''
        except Exception:
            return ''

    def extract_text_from_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ''
            if text:
                pages.append(text)
        return '\n\n'.join(pages).strip()

    def analyze_notes(self, text: str, title: str) -> Dict[str, Any]:
        prompt = f"""
You are an educational AI. Study the following student notes and return valid JSON only.
Title: {title}
Notes:
{text[:12000]}

Return this JSON structure:
{{
  "summary": "simple summary",
  "topics": [{{"name": "Topic name", "summary": "short explanation", "difficulty_level": "easy/medium/hard", "study_time_hours": 1.0}}],
  "difficulty_level": "easy|medium|hard",
  "estimated_study_time_hours": 2.5,
  "learning_plan": [{{"day": 1, "task": "Review chapter one"}}]
}}
"""
        raw = self._call_model(prompt)
        if raw:
            parsed = self._safe_json_loads(raw)
            if parsed:
                return self._normalize_analysis(parsed)
        return self._fallback_analysis(text, title)

    def generate_lecture(self, topic_name: str, note_text: str, topic_summary: str) -> str:
        prompt = f"""
You are a friendly teacher. Explain the topic below in simple language for a student.
Topic: {topic_name}
Notes: {note_text[:6000]}
Topic Summary: {topic_summary}
Return a short, student-friendly lecture text.
"""
        raw = self._call_model(prompt)
        if raw:
            return raw.strip()
        return (
            f"{topic_name} is introduced in a simple, student-friendly way. "
            f"Review the key ideas from your uploaded notes and focus on the main concepts first. "
            f"Break the topic into smaller chunks and revise it gradually to build confidence."
        )

    def generate_test_questions(self, topic_name: str, note_text: str) -> List[Dict[str, Any]]:
        prompt = f"""
Create 4 short questions from the uploaded notes. Return valid JSON only.
Topic: {topic_name}
Notes: {note_text[:8000]}
JSON format:
[{{"type": "mcq", "question": "...", "options": ["A", "B", "C", "D"], "answer": "A"}}, {{"type": "short", "question": "...", "answer": "..."}}]
"""
        raw = self._call_model(prompt)
        if raw:
            parsed = self._safe_json_loads(raw)
            if isinstance(parsed, list):
                return parsed[:4]
        return [
            {
                'type': 'mcq',
                'question': f'What is the main idea of {topic_name}?',
                'options': ['Key concept', 'Extra detail', 'Irrelevant point', 'None'],
                'answer': 'Key concept',
            },
            {
                'type': 'short',
                'question': f'Explain {topic_name} in one sentence.',
                'answer': 'Use the uploaded notes to explain the concept clearly.',
            },
        ]

    def chat(self, messages: List[Dict[str, str]], note_text: str, topics: List[Dict[str, Any]]) -> str:
        # Build a conversation-aware prompt that only uses the uploaded notes as source material.
        # Keep only the last several messages to keep the prompt size reasonable.
        recent = (messages or [])[-8:]
        convo_lines = []
        for m in recent:
            role = m.get('role') or 'user'
            text = (m.get('message') or '').strip()
            if not text:
                continue
            convo_lines.append(f"{role.upper()}: {text}")

        convo_text = '\n'.join(convo_lines)
        prompt = f"""
You are a strict study assistant. You must answer the student's questions using ONLY the uploaded notes provided below.
If the answer cannot be found verbatim or inferred directly from the notes, respond exactly with: Not in your notes.
Do not hallucinate, do not add outside knowledge, and keep answers concise.

Conversation:
{convo_text}

Notes:
{note_text[:16000]}

Topics: {json.dumps(topics[:10])}

Please provide a single short answer corresponding to the last user message.
"""
        raw = self._call_model(prompt)
        if raw:
            response = raw.strip()
            if response:
                return response
        
        # Fallback: If no API response but we have note content, provide helpful response
        if note_text and len(note_text.strip()) > 100:
            first_lines = '\n'.join(note_text.split('\n')[:3]).strip()
            return f"I found {len(note_text.split())} words in your notes. Please set GEMINI_API_KEY environment variable for AI-powered responses. Your notes start with: {first_lines}..."
        
        return "Not in your notes"

    def create_embeddings(self, text: str, chunk_size: int = 2000) -> List[Dict[str, Any]]:
        """
        Create simple deterministic embeddings by chunking text and hashing each chunk.
        This provides a persisted representation for basic semantic retrieval without external vector DBs.
        """
        logger = logging.getLogger(__name__)
        if not text:
            return []
        # naive chunking by characters to keep chunks under size
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        embeddings = []
        for idx, chunk in enumerate(chunks, start=1):
            h = hashlib.sha256(chunk.encode('utf-8')).hexdigest()
            embeddings.append({'id': f'chunk_{idx}', 'hash': h, 'text': chunk[:chunk_size]})
        logger.debug('Created %d embedding chunks', len(embeddings))
        return embeddings

    def _normalize_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        topics = []
        for index, topic in enumerate(payload.get('topics', []) or []):
            topics.append({
                'name': str(topic.get('name') or f'Topic {index + 1}'),
                'summary': str(topic.get('summary') or ''),
                'difficulty_level': str(topic.get('difficulty_level') or payload.get('difficulty_level') or 'medium'),
                'study_time_hours': float(topic.get('study_time_hours') or 1.0),
            })
        return {
            'summary': str(payload.get('summary') or ''),
            'topics': topics or [{'name': 'Main Topic', 'summary': 'Review the uploaded notes', 'difficulty_level': 'medium', 'study_time_hours': 1.0}],
            'difficulty_level': str(payload.get('difficulty_level') or 'medium'),
            'estimated_study_time_hours': float(payload.get('estimated_study_time_hours') or 2.0),
            'learning_plan': payload.get('learning_plan') or [{'day': 1, 'task': 'Review notes and revise key concepts'}],
        }

    def _fallback_analysis(self, text: str, title: str) -> Dict[str, Any]:
        cleaned = re.sub(r'\s+', ' ', text).strip()
        sentence = cleaned[:250] if cleaned else title
        topics = []
        for index, line in enumerate(re.split(r'(?<!\w)(?:Topic|Chapter|Lesson)\s*[:\-]?', cleaned)[:4], start=1):
            if line.strip():
                topics.append({
                    'name': f'Topic {index}',
                    'summary': line.strip()[:180],
                    'difficulty_level': 'medium',
                    'study_time_hours': 1.0,
                })
        if not topics:
            topics.append({
                'name': title or 'Main Topic',
                'summary': sentence,
                'difficulty_level': 'medium',
                'study_time_hours': 1.0,
            })
        return {
            'summary': f'Highlights from {title}: {sentence[:220]}',
            'topics': topics,
            'difficulty_level': 'medium',
            'estimated_study_time_hours': 2.0,
            'learning_plan': [{'day': 1, 'task': 'Review the uploaded notes and complete the first study task'}],
        }

    def _safe_json_loads(self, payload: str) -> Dict[str, Any]:
        cleaned = payload.strip()
        if cleaned.startswith('```'):
            cleaned = cleaned.strip('`')
        if cleaned.startswith('json'):
            cleaned = cleaned[4:].strip()
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {}


service = AIService()


def extract_text_from_pdf(file_path: str) -> str:
    return service.extract_text_from_pdf(file_path)


def analyze_notes(text: str, title: str) -> Dict[str, Any]:
    return service.analyze_notes(text, title)


def create_learning_flow(note: Note) -> Dict[str, Any]:
    topics = list(note.topics.all())
    if not topics:
        created_topics = []
        analysis = analyze_notes(note.original_text or '', note.title)
        for index, topic_data in enumerate(analysis.get('topics', []) or [], start=1):
            topic = Topic.objects.create(
                note=note,
                name=topic_data.get('name') or f'Topic {index}',
                summary=topic_data.get('summary') or '',
                difficulty_level=topic_data.get('difficulty_level') or 'medium',
                study_time_hours=topic_data.get('study_time_hours') or 1.0,
                order=index,
            )
            created_topics.append(topic)
        topics = created_topics

    tasks = []
    lectures = []
    for index, topic in enumerate(topics, start=1):
        task = DailyTask.objects.create(
            note=note,
            topic=topic,
            title=f'{topic.name} - {topic.study_time_hours}h study',
            task_type='Study',
            study_time_hours=topic.study_time_hours,
            status='unlocked' if index == 1 else 'locked',
            sequence_order=index,
        )
        tasks.append(task)

        lecture = Lecture.objects.create(
            note=note,
            topic=topic,
            title=f'Lecture: {topic.name}',
            content=service.generate_lecture(topic.name, note.original_text or '', topic.summary),
            status='unlocked' if index == 1 else 'locked',
            sequence_order=index,
        )
        lectures.append(lecture)

    progress, _ = UserProgress.objects.get_or_create(user=note.user, note=note)
    progress.completed_tasks = 0
    progress.completed_lectures = 0
    progress.completed_tests = 0
    progress.save(update_fields=['completed_tasks', 'completed_lectures', 'completed_tests'])
    return {'tasks': tasks, 'lectures': lectures, 'progress': progress}


async def process_note_in_background(note: Note) -> None:
    note.processing_status = 'processing'
    note.save(update_fields=['processing_status'])
    text = await asyncio.to_thread(extract_text_from_pdf, str(note.file.path))
    analysis = await asyncio.to_thread(analyze_notes, text, note.title)
    note.original_text = text
    note.summary = analysis.get('summary', '')
    note.difficulty_level = analysis.get('difficulty_level', 'medium')
    note.estimated_study_time_hours = analysis.get('estimated_study_time_hours', 2.0)
    note.learning_plan = analysis.get('learning_plan', [])
    # create embeddings and persist them so chat and retrieval can use them
    try:
        embeddings = service.create_embeddings(text)
        note.embeddings = embeddings
    except Exception:
        embeddings = []
    note.processing_status = 'completed'
    note.save(update_fields=['original_text', 'summary', 'difficulty_level', 'estimated_study_time_hours', 'learning_plan', 'processing_status', 'embeddings'])
    create_learning_flow(note)


def create_test_for_lecture(lecture: Lecture) -> Test:
    if hasattr(lecture, 'test'):
        return lecture.test
    questions = service.generate_test_questions(lecture.topic.name if lecture.topic else lecture.title, lecture.note.original_text or '')
    return Test.objects.create(lecture=lecture, note=lecture.note, questions=questions)


def unlock_next_task(note: Note) -> bool:
    tasks = list(note.daily_tasks.all())
    completed = [task for task in tasks if task.status == 'completed']
    if not completed:
        return False
    next_task = next((task for task in sorted(tasks, key=lambda item: item.sequence_order) if task.status == 'locked'), None)
    if next_task:
        next_task.status = 'unlocked'
        next_task.save(update_fields=['status'])
        return True
    return False


def unlock_next_lecture(note: Note) -> bool:
    lectures = list(note.lectures.all())
    completed = [lecture for lecture in lectures if lecture.status == 'completed']
    if not completed:
        return False
    next_lecture = next((lecture for lecture in sorted(lectures, key=lambda item: item.sequence_order) if lecture.status == 'locked'), None)
    if next_lecture:
        next_lecture.status = 'unlocked'
        next_lecture.save(update_fields=['status'])
        return True
    return False

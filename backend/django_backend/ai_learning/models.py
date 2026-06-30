from decimal import Decimal

from django.conf import settings
from django.db import models


class Note(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='notes/%Y/%m/%d/', blank=True, null=True)
    original_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=30, blank=True)
    estimated_study_time_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    learning_plan = models.JSONField(default=list, blank=True)
    # Stored embeddings or vector chunks extracted from the note for semantic search.
    embeddings = models.JSONField(default=list, blank=True)
    completed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Topic(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=30, blank=True)
    study_time_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.note.title} :: {self.name}'


class DailyTask(models.Model):
    STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    TASK_CHOICES = [
        ('Study', 'Study'),
        ('Revise', 'Revise'),
        ('Practice', 'Practice'),
    ]

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='daily_tasks')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    title = models.CharField(max_length=255)
    task_type = models.CharField(max_length=20, choices=TASK_CHOICES, default='Study')
    study_time_hours = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='locked')
    sequence_order = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['sequence_order', 'id']

    def __str__(self):
        return self.title


class Lecture(models.Model):
    STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked'),
        ('completed', 'Completed'),
    ]

    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='lectures')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lectures', null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='locked')
    sequence_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Test(models.Model):
    lecture = models.OneToOneField(Lecture, on_delete=models.CASCADE, related_name='test')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='tests')
    questions = models.JSONField(default=list, blank=True)
    score = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Test for {self.lecture.title}'


class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='progress_records')
    completed_tasks = models.PositiveIntegerField(default=0)
    completed_lectures = models.PositiveIntegerField(default=0)
    completed_tests = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'note')

    def __str__(self):
        return f'{self.user.username} :: {self.note.title}'

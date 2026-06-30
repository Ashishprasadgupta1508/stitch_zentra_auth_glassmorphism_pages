from django.contrib import admin

from .models import DailyTask, Lecture, Note, Test, Topic, UserProgress


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'processing_status', 'difficulty_level', 'estimated_study_time_hours', 'created_at')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'note', 'difficulty_level', 'study_time_hours', 'order')


@admin.register(DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'note', 'topic', 'task_type', 'status', 'sequence_order')


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'note', 'topic', 'status', 'sequence_order')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('lecture', 'note', 'score', 'completed')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'note', 'completed_tasks', 'completed_lectures', 'completed_tests')

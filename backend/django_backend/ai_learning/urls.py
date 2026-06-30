from django.urls import path

from . import views

urlpatterns = [
    path('notes/', views.note_list, name='note-list'),
    path('notes/upload', views.upload_note, name='upload-note-exact'),
    path('notes/upload/', views.upload_note, name='upload-note'),
    path('notes/<int:note_id>/', views.note_detail, name='note-detail'),
    path('tasks/<int:note_id>', views.tasks_for_note, name='tasks-for-note-exact'),
    path('tasks/<int:note_id>/', views.tasks_for_note, name='tasks-for-note'),
    path('tasks/<int:task_id>/start', views.start_task, name='start-task-exact'),
    path('tasks/<int:task_id>/start/', views.start_task, name='start-task'),
    path('tasks/<int:task_id>/complete', views.complete_task, name='complete-task-exact'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete-task'),
    path('lecture/<int:topic_id>', views.lecture_for_topic, name='lecture-for-topic-exact'),
    path('lecture/<int:topic_id>/', views.lecture_for_topic, name='lecture-for-topic'),
    path('test/<int:topic_id>', views.test_for_topic, name='test-for-topic-exact'),
    path('test/<int:topic_id>/', views.test_for_topic, name='test-for-topic'),
    path('test/<int:topic_id>/submit', views.submit_test_for_topic, name='submit-test-for-topic-exact'),
    path('test/<int:topic_id>/submit/', views.submit_test_for_topic, name='submit-test-for-topic'),
    path('progress', views.progress_summary, name='progress-summary-exact'),
    path('progress/', views.progress_summary, name='progress-summary'),
    path('chat', views.chat_with_ai, name='chat-with-ai-exact'),
    path('chat/', views.chat_with_ai, name='chat-with-ai-public'),
    path('lectures/<int:lecture_id>/', views.lecture_detail, name='lecture-detail'),
    path('lectures/<int:lecture_id>/complete/', views.complete_lecture, name='complete-lecture'),
    path('tests/<int:test_id>/submit/', views.submit_test, name='submit-test'),
    path('insights/chat/', views.chat_with_ai, name='chat-with-ai'),
]

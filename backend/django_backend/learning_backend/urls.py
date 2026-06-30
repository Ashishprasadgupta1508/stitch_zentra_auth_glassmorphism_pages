from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

urlpatterns = [
    path('health/', lambda _request: JsonResponse({'ok': True, 'service': 'zentra-django-backend'})),
    path('admin/', admin.site.urls),
    path('api/', include('ai_learning.urls')),
]

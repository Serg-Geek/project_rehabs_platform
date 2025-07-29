"""
URL configuration for rehabs_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


# rehabs_platform/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from core.views import page_not_found
from .admin import admin_site

handler404 = page_not_found

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('core.urls')),  # Добавляем URL-маршруты для главной страницы
    path('facilities/', include('facilities.urls')),  # Добавляем URL-маршруты для учреждений
    path('staff/', include('staff.urls')),  # Добавляем URL-маршруты для специалистов
    path('users/', include('users.urls')),
    path('blog/', include('blog.urls')),
    path('requests/', include('requests.urls')),  # Добавляем URL-маршруты для заявок
    path('medical-services/', include('medical_services.urls')),
    path('recovery-stories/', include('recovery_stories.urls')),  # Добавляем URL-маршруты для историй выздоровления
    path('reviews/', include('reviews.urls')),
    path('content/', include('content.urls')),  # Добавляем URL-маршруты для контента
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

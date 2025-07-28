"""
Сигналы для автоматического логирования изменений моделей.

Предоставляет сигналы для:
- Логирования создания объектов
- Логирования изменения объектов
- Логирования удаления объектов
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .logging import database_logger, security_logger, business_logger


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """Логирование создания и изменения моделей."""
    # Исключаем системные модели
    excluded_models = [
        'admin_logs.AdminActionLog',
        'sessions.Session',
        'contenttypes.ContentType',
        'auth.Permission',
        'auth.Group',
    ]
    
    model_name = f"{sender._meta.app_label}.{sender._meta.model_name}"
    if model_name in excluded_models:
        return
    
    action = 'create' if created else 'update'
    
    # Получаем пользователя из контекста запроса
    user = None
    try:
        from django.contrib.auth.models import AnonymousUser
        from django.db import connection
        
        # Пытаемся получить пользователя из текущего запроса
        if hasattr(connection, 'request') and connection.request:
            user = getattr(connection.request, 'user', None)
            if isinstance(user, AnonymousUser):
                user = None
    except:
        pass
    
    # Проверяем, что у объекта есть id
    if hasattr(instance, 'id') and instance.id is not None:
        database_logger.log_model_change(
            model_name=model_name,
            action=action,
            object_id=instance.id,
            user=user
        )


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """Логирование удаления моделей."""
    # Исключаем системные модели
    excluded_models = [
        'admin_logs.AdminActionLog',
        'sessions.Session',
        'contenttypes.ContentType',
        'auth.Permission',
        'auth.Group',
    ]
    
    model_name = f"{sender._meta.app_label}.{sender._meta.model_name}"
    if model_name in excluded_models:
        return
    
    # Получаем пользователя из контекста запроса
    user = None
    try:
        from django.contrib.auth.models import AnonymousUser
        from django.db import connection
        
        if hasattr(connection, 'request') and connection.request:
            user = getattr(connection.request, 'user', None)
            if isinstance(user, AnonymousUser):
                user = None
    except:
        pass
    
    # Проверяем, что у объекта есть id
    if hasattr(instance, 'id') and instance.id is not None:
        database_logger.log_model_change(
            model_name=model_name,
            action='delete',
            object_id=instance.id,
            user=user
        )


@receiver(user_logged_in)
def log_user_login(sender, user, request, **kwargs):
    """
    Log successful user login.
    
    Args:
        sender: User model class
        user: User instance
        request: HTTP request object
        **kwargs: Additional keyword arguments
    """
    security_logger.log_login_attempt(
        username=user.username,
        success=True,
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    business_logger.log_user_action(
        user=user,
        action='login',
        details={'method': 'form'},
        ip_address=_get_client_ip(request)
    )


@receiver(user_logged_out)
def log_user_logout(sender, user, request, **kwargs):
    """
    Log user logout.
    
    Args:
        sender: User model class
        user: User instance
        request: HTTP request object
        **kwargs: Additional keyword arguments
    """
    if user:  # Проверяем, что user не None
        business_logger.log_user_action(
            user=user,
            action='logout',
            ip_address=_get_client_ip(request)
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request=None, **kwargs):
    """
    Log failed login attempt.
    
    Args:
        sender: User model class
        credentials: Login credentials
        request: HTTP request object (optional)
        **kwargs: Additional keyword arguments
    """
    username = credentials.get('username', 'unknown')
    security_logger.log_login_attempt(
        username=username,
        success=False,
        ip_address=_get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None
    )


def _get_client_ip(request):
    """
    Get client IP address.
    
    Args:
        request: HTTP request object
        
    Returns:
        str: Client IP address or None if request is None
    """
    if not request:
        return None
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip 
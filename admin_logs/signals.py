from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
import datetime
from .models import AdminActionLog, AccessLevel, UserAccess

def get_changed_fields(instance, old_instance=None):
    """
    Получение измененных полей между текущим и старым экземпляром
    """
    if not old_instance:
        return {}
    
    changed_fields = {}
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(instance, field_name)
        
        # Преобразуем datetime в строку ISO формата
        if isinstance(old_value, (datetime.datetime, datetime.date)):
            old_value = old_value.isoformat()
        if isinstance(new_value, (datetime.datetime, datetime.date)):
            new_value = new_value.isoformat()
        
        # Обрабатываем объекты моделей
        if hasattr(old_value, 'pk'):
            old_value = str(old_value)
        if hasattr(new_value, 'pk'):
            new_value = str(new_value)
            
        if old_value != new_value:
            changed_fields[field_name] = {
                'old': old_value,
                'new': new_value
            }
    return changed_fields

@receiver(pre_save)
def log_pre_save(sender, instance, **kwargs):
    """
    Логирование изменений перед сохранением
    """
    if not settings.ADMIN_LOGS['ENABLE_LOGGING']:
        return
    
    if f"{sender._meta.app_label}.{sender._meta.model_name}" in settings.ADMIN_LOGS['EXCLUDE_MODELS']:
        return
    
    if not any(f"{sender._meta.app_label}.*" in pattern for pattern in settings.ADMIN_LOGS['INCLUDE_MODELS']):
        return
    
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._old_instance = old_instance
    except sender.DoesNotExist:
        instance._old_instance = None

@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    """
    Логирование действий после сохранения
    """
    if not settings.ADMIN_LOGS['ENABLE_LOGGING']:
        return
    
    if f"{sender._meta.app_label}.{sender._meta.model_name}" in settings.ADMIN_LOGS['EXCLUDE_MODELS']:
        return
    
    if not any(f"{sender._meta.app_label}.*" in pattern for pattern in settings.ADMIN_LOGS['INCLUDE_MODELS']):
        return
    
    action = 'create' if created else 'update'
    changes = {}
    
    if not created and hasattr(instance, '_old_instance'):
        changes = get_changed_fields(instance, instance._old_instance)
    
    AdminActionLog.objects.create(
        user=instance._current_user if hasattr(instance, '_current_user') else None,
        action=action,
        app_label=sender._meta.app_label,
        model_name=sender._meta.model_name,
        object_id=instance.pk,
        changes=changes,
        access_level=None,
        ip_address=instance._current_ip if hasattr(instance, '_current_ip') else None
    )

@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    """
    Логирование действий после удаления
    """
    if not settings.ADMIN_LOGS['ENABLE_LOGGING']:
        return
    
    if f"{sender._meta.app_label}.{sender._meta.model_name}" in settings.ADMIN_LOGS['EXCLUDE_MODELS']:
        return
    
    if not any(f"{sender._meta.app_label}.*" in pattern for pattern in settings.ADMIN_LOGS['INCLUDE_MODELS']):
        return
    
    AdminActionLog.objects.create(
        user=instance._current_user if hasattr(instance, '_current_user') else None,
        action='delete',
        app_label=sender._meta.app_label,
        model_name=sender._meta.model_name,
        object_id=instance.pk,
        access_level=None,
        ip_address=instance._current_ip if hasattr(instance, '_current_ip') else None
    ) 
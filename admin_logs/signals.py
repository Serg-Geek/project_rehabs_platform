from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
import datetime
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile
from .models import AdminActionLog, AccessLevel, UserAccess

def get_changed_fields(instance, old_instance=None):
    """
    Get changed fields between current and old instance.
    
    Args:
        instance: Current model instance
        old_instance: Previous model instance
        
    Returns:
        dict: Dictionary of changed fields with old and new values
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
        
        # Обрабатываем файловые объекты
        if isinstance(old_value, (File, UploadedFile)):
            old_value = old_value.name if hasattr(old_value, 'name') and old_value.name else str(old_value)
        if isinstance(new_value, (File, UploadedFile)):
            new_value = new_value.name if hasattr(new_value, 'name') and new_value.name else str(new_value)
        
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
    Log changes before saving.
    
    Args:
        sender: Model class
        instance: Model instance
        **kwargs: Additional keyword arguments
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
    Log actions after saving.
    
    Args:
        sender: Model class
        instance: Model instance
        created: Whether this is a new instance
        **kwargs: Additional keyword arguments
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
    
    log_entry = AdminActionLog(
        user=instance._current_user if hasattr(instance, '_current_user') else None,
        action=action,
        app_label=sender._meta.app_label,
        model_name=sender._meta.model_name,
        object_id=instance.pk,
        access_level=None,
        ip_address=instance._current_ip if hasattr(instance, '_current_ip') else None
    )
    log_entry.save_changes(changes)
    log_entry.save()

@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    """
    Log actions after deletion.
    
    Args:
        sender: Model class
        instance: Model instance
        **kwargs: Additional keyword arguments
    """
    if not settings.ADMIN_LOGS['ENABLE_LOGGING']:
        return
    
    if f"{sender._meta.app_label}.{sender._meta.model_name}" in settings.ADMIN_LOGS['EXCLUDE_MODELS']:
        return
    
    if not any(f"{sender._meta.app_label}.*" in pattern for pattern in settings.ADMIN_LOGS['INCLUDE_MODELS']):
        return
    
    log_entry = AdminActionLog(
        user=instance._current_user if hasattr(instance, '_current_user') else None,
        action='delete',
        app_label=sender._meta.app_label,
        model_name=sender._meta.model_name,
        object_id=instance.pk,
        access_level=None,
        ip_address=instance._current_ip if hasattr(instance, '_current_ip') else None
    )
    log_entry.save_changes({})
    log_entry.save() 
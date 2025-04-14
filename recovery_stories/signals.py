from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import AdminActionLog, RecoveryStory

User = get_user_model()

def get_changed_fields(instance, old_instance=None):
    """
    Получение измененных полей
    """
    if not old_instance:
        return {}
    
    changed_fields = {}
    for field in instance._meta.fields:
        old_value = getattr(old_instance, field.name)
        new_value = getattr(instance, field.name)
        if old_value != new_value:
            changed_fields[field.name] = {
                'old': old_value,
                'new': new_value
            }
    return changed_fields

@receiver(pre_save)
def log_pre_save(sender, instance, **kwargs):
    """
    Логирование перед сохранением
    """
    if not issubclass(sender, (RecoveryStory,)):
        return
    
    if instance.pk:  # Обновление
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._changed_fields = get_changed_fields(instance, old_instance)
        except sender.DoesNotExist:
            instance._changed_fields = {}

@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    """
    Логирование после сохранения
    """
    if not issubclass(sender, (RecoveryStory,)):
        return
    
    user = kwargs.get('user')
    if not user or not user.is_staff:
        return
    
    content_type = ContentType.objects.get_for_model(instance)
    
    if created:
        # Логирование создания
        AdminActionLog.objects.create(
            user=user,
            action='create',
            content_type=content_type,
            object_id=instance.pk,
            new_value=str(instance)
        )
    else:
        # Логирование изменений
        changed_fields = getattr(instance, '_changed_fields', {})
        for field_name, values in changed_fields.items():
            AdminActionLog.objects.create(
                user=user,
                action='update',
                content_type=content_type,
                object_id=instance.pk,
                field_name=field_name,
                old_value=str(values['old']),
                new_value=str(values['new'])
            )

@receiver(post_delete)
def log_post_delete(sender, instance, **kwargs):
    """
    Логирование после удаления
    """
    if not issubclass(sender, (RecoveryStory,)):
        return
    
    user = kwargs.get('user')
    if not user or not user.is_staff:
        return
    
    content_type = ContentType.objects.get_for_model(instance)
    AdminActionLog.objects.create(
        user=user,
        action='delete',
        content_type=content_type,
        object_id=instance.pk,
        old_value=str(instance)
    ) 
    
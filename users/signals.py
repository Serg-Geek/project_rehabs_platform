from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import UserProfile
from .models import UserActionLog

User = get_user_model()


def get_changed_fields(current_instance, old_instance):
    """Получение измененных полей"""
    if not old_instance:
        return {}
    
    changed_fields = {}
    for field in current_instance._meta.fields:
        old_value = getattr(old_instance, field.name)
        new_value = getattr(current_instance, field.name)
        if old_value != new_value:
            changed_fields[field.name] = {
                'old': old_value,
                'new': new_value
            }
    return changed_fields


@receiver(pre_save, sender=User)
def log_pre_save(sender, instance, **kwargs):
    """Логирование изменений перед сохранением"""
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            instance._old_instance = old_instance
        except User.DoesNotExist:
            instance._old_instance = None


@receiver(post_save, sender=User)
def handle_user_post_save(sender, instance, created, **kwargs):
    """Обработка всех действий после сохранения пользователя"""
    # Логирование
    if hasattr(instance, '_old_instance'):
        old_instance = instance._old_instance
        changed_fields = get_changed_fields(instance, old_instance)
    else:
        changed_fields = {}
    
    if created:
        action = 'create'
        details = f'Создан новый пользователь: {instance.username}'
        # Создание профиля
        UserProfile.objects.create(user=instance)
    else:
        action = 'update'
        details = f'Обновлен пользователь: {instance.username}'
        if changed_fields:
            details += f'\nИзмененные поля: {changed_fields}'
        # Сохранение профиля
        if hasattr(instance, 'profile'):
            instance.profile.save()
    
    # Логирование действий
    current_user = getattr(instance, '_current_user', None)
    if current_user and current_user.is_staff:
        UserActionLog.objects.create(
            user=current_user,
            action=action,
            model_name='User',
            object_id=instance.pk,
            details=details
        )


@receiver(post_delete, sender=User)
def log_post_delete(sender, instance, **kwargs):
    """Логирование действий после удаления"""
    # Проверяем, является ли текущий пользователь сотрудником
    current_user = getattr(instance, '_current_user', None)
    if current_user and current_user.is_staff:
        UserActionLog.objects.create(
            user=current_user,
            action='delete',
            model_name='User',
            object_id=instance.pk,
            details=f'Удален пользователь: {instance.username}'
        ) 
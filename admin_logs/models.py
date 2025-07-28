from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.files.base import File
from django.core.files.uploadedfile import UploadedFile
import json

User = get_user_model()

class AccessLevel(models.Model):
    class LevelType(models.TextChoices):
        SUPERUSER = 'superuser', _('Суперюзер')
        CONTENT_ADMIN = 'content_admin', _('Администратор контента')
        REQUESTS_ADMIN = 'requests_admin', _('Администратор заявок')

    name = models.CharField(max_length=50, verbose_name=_('Название'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Код'))
    level_type = models.CharField(
        max_length=20,
        choices=LevelType.choices,
        default=LevelType.CONTENT_ADMIN,
        verbose_name=_('Тип уровня')
    )
    description = models.TextField(verbose_name=_('Описание'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_access_levels',
        verbose_name=_('Создан пользователем')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Уровень доступа')
        verbose_name_plural = _('Уровни доступа')

    def __str__(self):
        return self.name

class AppPermission(models.Model):
    app_label = models.CharField(max_length=100, verbose_name=_('Приложение'))
    access_level = models.ForeignKey(
        AccessLevel,
        on_delete=models.CASCADE,
        related_name='app_permissions',
        verbose_name=_('Уровень доступа')
    )
    can_view = models.BooleanField(default=False, verbose_name=_('Может просматривать'))
    can_add = models.BooleanField(default=False, verbose_name=_('Может добавлять'))
    can_change = models.BooleanField(default=False, verbose_name=_('Может изменять'))
    can_delete = models.BooleanField(default=False, verbose_name=_('Может удалять'))
    can_assign_responsible = models.BooleanField(
        default=False,
        verbose_name=_('Может назначать ответственных')
    )
    can_change_status = models.BooleanField(
        default=False,
        verbose_name=_('Может изменять статус')
    )

    class Meta:
        verbose_name = _('Разрешение приложения')
        verbose_name_plural = _('Разрешения приложений')
        unique_together = ['app_label', 'access_level']

    def __str__(self):
        return f"{self.app_label} - {self.access_level}"

class UserAccess(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name=_('Пользователь')
    )
    access_level = models.ForeignKey(
        AccessLevel,
        on_delete=models.CASCADE,
        related_name='user_accesses',
        verbose_name=_('Уровень доступа')
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_accesses',
        verbose_name=_('Назначен пользователем')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    valid_from = models.DateTimeField(verbose_name=_('Действует с'))
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Действует до')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Доступ пользователя')
        verbose_name_plural = _('Доступы пользователей')

    def __str__(self):
        return f"{self.user} - {self.access_level}"

class AdminActionLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions',
        verbose_name=_('Пользователь')
    )
    action = models.CharField(max_length=50, verbose_name=_('Действие'))
    app_label = models.CharField(max_length=100, verbose_name=_('Приложение'))
    model_name = models.CharField(max_length=100, verbose_name=_('Модель'))
    object_id = models.PositiveIntegerField(verbose_name=_('ID объекта'))
    changes = models.JSONField(default=dict, verbose_name=_('Изменения'))
    access_level = models.ForeignKey(
        AccessLevel,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions',
        verbose_name=_('Уровень доступа')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP-адрес')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Лог действий администратора')
        verbose_name_plural = _('Логи действий администраторов')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"

    def save_changes(self, changes_dict):
        """
        Безопасно сохраняет изменения, обрабатывая файловые объекты
        """
        def serialize_value(value):
            if isinstance(value, (File, UploadedFile)):
                return value.name if hasattr(value, 'name') and value.name else str(value)
            elif hasattr(value, 'pk'):
                return str(value)
            elif isinstance(value, dict):
                return {k: serialize_value(v) for k, v in value.items()}
            elif isinstance(value, (list, tuple)):
                return [serialize_value(v) for v in value]
            else:
                return value
        
        # Сериализуем изменения
        serialized_changes = serialize_value(changes_dict)
        self.changes = serialized_changes

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from medical_services.models import Service
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Request(TimeStampedModel):
    """
    Заявка на лечение
    """
    class Status(models.TextChoices):
        NEW = 'new', _('Новая')
        IN_PROGRESS = 'in_progress', _('В обработке')
        APPROVED = 'approved', _('Одобрена')
        REJECTED = 'rejected', _('Отклонена')
        COMPLETED = 'completed', _('Завершена')

    class AddictionType(models.TextChoices):
        ALCOHOL = 'alcohol', _('Алкоголь')
        DRUGS = 'drugs', _('Наркотики')
        GAMBLING = 'gambling', _('Игровая зависимость')
        OTHER = 'other', _('Другое')

    class ContactType(models.TextChoices):
        ANONYMOUS = 'anonymous', _('Анонимно')
        PSEUDONYM = 'pseudonym', _('Под псевдонимом')
        REAL_NAME = 'real_name', _('Под реальным именем')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_('Статус')
    )
    addiction_type = models.CharField(
        max_length=20,
        choices=AddictionType.choices,
        verbose_name=_('Тип зависимости')
    )
    contact_type = models.CharField(
        max_length=20,
        choices=ContactType.choices,
        default=ContactType.ANONYMOUS,
        verbose_name=_('Тип контакта')
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Имя')
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Фамилия')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон')
    )
    pseudonym = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Псевдоним')
    )
    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Контактное лицо')
    )
    emergency_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон контактного лица')
    )
    medical_history = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('История болезни')
    )
    treatment_plan = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('План лечения')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Заметки')
    )
    responsible_staff = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests',
        verbose_name=_('Ответственный сотрудник')
    )

    class Meta:
        verbose_name = _('Заявка')
        verbose_name_plural = _('Заявки')
        ordering = ['-created_at']

    def __str__(self):
        if self.contact_type == self.ContactType.ANONYMOUS:
            return f"Анонимная заявка #{self.id}"
        elif self.contact_type == self.ContactType.PSEUDONYM and self.pseudonym:
            return f"{self.pseudonym} (псевдоним)"
        elif self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        return f"Заявка #{self.id}"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.last_name} {self.first_name}"
        return "-"

class AnonymousRequest(TimeStampedModel):
    """
    Анонимные заявки от пользователей
    """
    class RequestType(models.TextChoices):
        CONSULTATION = 'consultation', 'Консультация'
        TREATMENT = 'treatment', 'Лечение'
        REHABILITATION = 'rehabilitation', 'Реабилитация'
        PARTNER = 'partner', 'Партнерство'
        OTHER = 'other', 'Другое'

    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'В обработке'
        WAITING_COMMISSION = 'waiting_commission', 'Ожидание комиссии'
        COMMISSION_RECEIVED = 'commission_received', 'Комиссия получена'
        TREATMENT_STARTED = 'treatment_started', 'Лечение начато (опционально)'
        TREATMENT_COMPLETED = 'treatment_completed', 'Лечение завершено (опционально)'
        CANCELLED = 'cancelled', 'Отменена'
        CLOSED = 'closed', 'Закрыта'

    class Priority(models.TextChoices):
        LOW = 'low', 'Низкий'
        MEDIUM = 'medium', 'Средний'
        HIGH = 'high', 'Высокий'
        URGENT = 'urgent', 'Срочный'

    request_type = models.CharField('Тип заявки', max_length=20, choices=RequestType.choices)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.NEW)
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True, null=True)
    organization = models.CharField('Организация', max_length=200, blank=True, null=True)
    message = models.TextField('Сообщение')
    patient_name = models.CharField('Имя пациента', max_length=100, blank=True, null=True)
    patient_age = models.IntegerField('Возраст пациента', blank=True, null=True)
    preferred_contact_time = models.CharField('Предпочтительное время для связи', max_length=100, blank=True, null=True)
    
    # Изменяем поле preferred_facility на GenericForeignKey для поддержки разных типов учреждений
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Тип контента')
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('ID объекта')
    )
    preferred_facility = GenericForeignKey('content_type', 'object_id')
    
    preferred_service = models.CharField('Предпочтительная услуга', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    # Новые поля для комиссии
    commission_amount = models.DecimalField('Сумма комиссии', max_digits=10, decimal_places=2, blank=True, null=True)
    commission_received_date = models.DateField('Дата получения комиссии', blank=True, null=True)
    commission_document = models.FileField('Документ комиссии', upload_to='commissions/', blank=True, null=True)

    # Поля для отслеживания пользователей
    created_by = models.ForeignKey(
        'auth.User',
        verbose_name='Создано пользователем',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_requests'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        verbose_name='Обновлено пользователем',
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_requests'
    )
    assigned_to = models.ForeignKey(
        'auth.User',
        verbose_name='Назначено',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )

    # Поле приоритета
    priority = models.CharField(
        'Приоритет',
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    class Meta:
        verbose_name = 'Анонимная заявка'
        verbose_name_plural = 'Анонимные заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.id} - {self.name} - {self.get_request_type_display()} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        if self.status == self.Status.COMMISSION_RECEIVED and not self.commission_received_date:
            self.commission_received_date = timezone.now().date()
            
        super().save(*args, **kwargs)

class RequestNote(TimeStampedModel):
    """
    Заметки к заявкам
    """
    request = models.ForeignKey(
        AnonymousRequest,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Заявка')
    )
    text = models.TextField(
        verbose_name=_('Текст')
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name=_('Важное')
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='request_notes',
        verbose_name=_('Создано пользователем')
    )

    class Meta:
        verbose_name = _('Заметка к заявке')
        verbose_name_plural = _('Заметки к заявкам')
        ordering = ['-created_at']

    def __str__(self):
        return f"Заметка к заявке #{self.request.id} - {self.request.name}"

class RequestStatusHistory(models.Model):
    """
    История изменений статуса заявки
    """
    request = models.ForeignKey(
        AnonymousRequest,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Заявка'
    )
    old_status = models.CharField('Старый статус', max_length=20, choices=AnonymousRequest.Status.choices)
    new_status = models.CharField('Новый статус', max_length=20, choices=AnonymousRequest.Status.choices)
    comment = models.TextField('Комментарий', blank=True, null=True)
    changed_at = models.DateTimeField('Дата изменения', auto_now_add=True)
    changed_by = models.ForeignKey(
        'auth.User',
        verbose_name='Изменено пользователем',
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes'
    )

    class Meta:
        verbose_name = 'История статусов'
        verbose_name_plural = 'История статусов'
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.request.name} - {self.old_status} -> {self.new_status}'

class RequestActionLog(TimeStampedModel):
    class Action(models.TextChoices):
        CREATE = 'create', _('Создание')
        UPDATE = 'update', _('Обновление')
        STATUS_CHANGE = 'status_change', _('Изменение статуса')
        COMMISSION = 'commission', _('Работа с комиссией')
        NOTE = 'note', _('Добавление заметки')
        ASSIGN = 'assign', _('Назначение')
        OTHER = 'other', _('Другое')

    request = models.ForeignKey(
        AnonymousRequest,
        on_delete=models.CASCADE,
        related_name='action_logs',
        verbose_name=_('Заявка')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='request_actions',
        verbose_name=_('Пользователь')
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name=_('Действие')
    )
    details = models.TextField(verbose_name=_('Детали'))

    class Meta:
        verbose_name = _('Лог действий')
        verbose_name_plural = _('Логи действий')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.request.name}"

from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from medical_services.models import Service
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class AnonymousRequest(TimeStampedModel):
    """
    Анонимные заявки от пользователей
    """
    class RequestType(models.TextChoices):
        CONSULTATION = 'consultation', _('Консультация')
        TREATMENT = 'treatment', _('Лечение')
        REHABILITATION = 'rehabilitation', _('Реабилитация')
        PARTNER = 'partner', _('Партнерство')
        OTHER = 'other', _('Другое')

    class Status(models.TextChoices):
        NEW = 'new', _('Новая')
        IN_PROGRESS = 'in_progress', _('В обработке')
        WAITING_COMMISSION = 'waiting_commission', _('Ожидание комиссии')
        COMMISSION_RECEIVED = 'commission_received', _('Комиссия получена')
        TREATMENT_STARTED = 'treatment_started', _('Лечение начато')
        TREATMENT_COMPLETED = 'treatment_completed', _('Лечение завершено')
        CANCELLED = 'cancelled', _('Отменена')
        CLOSED = 'closed', _('Закрыта')

    class Priority(models.TextChoices):
        LOW = 'low', _('Низкий')
        MEDIUM = 'medium', _('Средний')
        HIGH = 'high', _('Высокий')
        URGENT = 'urgent', _('Срочный')
        
    class Source(models.TextChoices):
        WEBSITE_FORM = 'website_form', _('Веб-форма')
        PHONE_CALL = 'phone_call', _('Телефонный звонок')
        EMAIL = 'email', _('Email')
        OFFLINE = 'offline', _('Очное обращение')
        OTHER = 'other', _('Другое')

    request_type = models.CharField(
        _('Тип заявки'),
        max_length=20,
        choices=RequestType.choices
    )
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    priority = models.CharField(
        _('Приоритет'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    source = models.CharField(
        _('Источник заявки'),
        max_length=20,
        choices=Source.choices,
        default=Source.WEBSITE_FORM
    )
    name = models.CharField(
        _('Имя'),
        max_length=100
    )
    phone = models.CharField(
        _('Телефон'),
        max_length=20
    )
    email = models.EmailField(
        _('Email'),
        blank=True,
        null=True
    )
    organization = models.CharField(
        _('Организация'),
        max_length=200,
        blank=True,
        null=True
    )
    message = models.TextField(
        _('Сообщение')
    )
    patient_name = models.CharField(
        _('Имя пациента'),
        max_length=100,
        blank=True,
        null=True
    )
    patient_age = models.IntegerField(
        _('Возраст пациента'),
        blank=True,
        null=True
    )
    preferred_contact_time = models.CharField(
        _('Предпочтительное время для связи'),
        max_length=100,
        blank=True,
        null=True
    )
    
    # Поля для учреждения (новые)
    organization_type = models.ForeignKey(
        'facilities.OrganizationType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Тип организации')
    )
    assigned_organization = models.CharField(
        _('Назначенная организация'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Сначала выберите тип организации, сохраните заявку, затем выберите организацию из списка')
    )
    
    # Поля для учреждения (старые - оставляем для совместимости)
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
    
    preferred_service = models.CharField(
        _('Предпочтительная услуга'),
        max_length=200,
        blank=True,
        null=True
    )

    # Поля для комиссии
    commission_amount = models.DecimalField(
        _('Сумма комиссии'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    commission_received_date = models.DateField(
        _('Дата получения комиссии'),
        blank=True,
        null=True
    )
    commission_document = models.FileField(
        _('Документ комиссии'),
        upload_to='commissions/',
        blank=True,
        null=True
    )

    # Поля для отслеживания
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Создано пользователем'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_requests'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Обновлено пользователем'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_requests'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Назначено'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )

    class Meta:
        verbose_name = _('Анонимная заявка')
        verbose_name_plural = _('Анонимные заявки')
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.id} - {self.name} - {self.get_request_type_display()} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        if self.status == self.Status.COMMISSION_RECEIVED and not self.commission_received_date:
            self.commission_received_date = timezone.now().date()
        
        # Проверка на пустые поля name и phone
        if not self.name:
            self.name = "Анонимный пользователь"
        
        if not self.message:
            self.message = "Заявка без содержания"
            
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
        settings.AUTH_USER_MODEL,
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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes',
        verbose_name='Изменено пользователем'
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
        settings.AUTH_USER_MODEL,
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

class RequestTemplate(models.Model):
    """
    Шаблоны для типовых заявок
    """
    name = models.CharField(_('Название шаблона'), max_length=100)
    request_type = models.CharField(
        _('Тип заявки'),
        max_length=20,
        choices=AnonymousRequest.RequestType.choices
    )
    template_text = models.TextField(_('Шаблонный текст'))
    is_active = models.BooleanField(_('Активен'), default=True)
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Создано пользователем'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates'
    )
    
    class Meta:
        verbose_name = _('Шаблон заявки')
        verbose_name_plural = _('Шаблоны заявок')
        ordering = ['name']
        
    def __str__(self):
        return self.name

class DependentRequest(TimeStampedModel):
    """
    Заявки от зависимых
    """
    class AddictionType(models.TextChoices):
        ALCOHOL = 'alcohol', _('Алкоголь')
        DRUGS = 'drugs', _('Наркотики')
        GAMBLING = 'gambling', _('Игровая зависимость')
        OTHER = 'other', _('Другое')

    class ContactType(models.TextChoices):
        ANONYMOUS = 'anonymous', _('Анонимно')
        PSEUDONYM = 'pseudonym', _('Под псевдонимом')
        REAL_NAME = 'real_name', _('Под реальным именем')

    class Status(models.TextChoices):
        NEW = 'new', _('Новая')
        IN_PROGRESS = 'in_progress', _('В обработке')
        WAITING_COMMISSION = 'waiting_commission', _('Ожидание комиссии')
        COMMISSION_RECEIVED = 'commission_received', _('Комиссия получена')
        TREATMENT_STARTED = 'treatment_started', _('Лечение начато')
        TREATMENT_COMPLETED = 'treatment_completed', _('Лечение завершено')
        CANCELLED = 'cancelled', _('Отменена')
        CLOSED = 'closed', _('Закрыта')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_('Статус')
    )
    addiction_type = models.CharField(
        max_length=20,
        choices=AddictionType.choices,
        default=AddictionType.OTHER,
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
    pseudonym = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Псевдоним')
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Телефон')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email')
    )
    age = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Возраст')
    )
    addiction_duration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Длительность зависимости')
    )
    previous_treatment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Предыдущее лечение')
    )
    current_condition = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Текущее состояние')
    )
    preferred_treatment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Предпочтительный вид лечения')
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
    extra_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Дополнительные заметки')
    )
    responsible_staff = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_requests',
        verbose_name=_('Ответственный сотрудник')
    )
    
    # Поля для учреждения
    organization_type = models.ForeignKey(
        'facilities.OrganizationType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Тип организации')
    )
    assigned_organization = models.CharField(
        _('Назначенная организация'),
        max_length=200,
        blank=True,
        null=True,
        help_text=_('Сначала выберите тип организации, сохраните заявку, затем выберите организацию из списка')
    )

    class Meta:
        verbose_name = _('Заявка от зависимого')
        verbose_name_plural = _('Заявки от зависимых')
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
        
    def save(self, *args, **kwargs):
        # Проверка на обязательный телефон
        if not self.phone:
            raise ValueError(_('Телефон обязателен для заявки'))
            
        # Если контакт анонимный и нет имени, устанавливаем псевдоним
        if self.contact_type == self.ContactType.ANONYMOUS and not self.pseudonym:
            self.pseudonym = "Аноним"
        
        super().save(*args, **kwargs)

class DependentRequestNote(TimeStampedModel):
    """
    Заметки к заявкам от зависимых
    """
    request = models.ForeignKey(
        'DependentRequest',
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Заявка от зависимого')
    )
    text = models.TextField(
        verbose_name=_('Текст')
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name=_('Важное')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dependent_request_notes',
        verbose_name=_('Создано пользователем')
    )

    class Meta:
        verbose_name = _('Заметка к заявке от зависимого')
        verbose_name_plural = _('Заметки к заявкам от зависимых')
        ordering = ['-created_at']

    def __str__(self):
        return f"Заметка к заявке #{self.request.id} - {self.request.get_full_name()}"

class DependentRequestStatusHistory(models.Model):
    """
    История изменений статуса заявки от зависимого
    """
    request = models.ForeignKey(
        'DependentRequest',
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Заявка от зависимого')
    )
    old_status = models.CharField('Старый статус', max_length=20, choices=DependentRequest.Status.choices)
    new_status = models.CharField('Новый статус', max_length=20, choices=DependentRequest.Status.choices)
    comment = models.TextField('Комментарий', blank=True, null=True)
    changed_at = models.DateTimeField('Дата изменения', auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dependent_status_changes',
        verbose_name=_('Изменено пользователем')
    )

    class Meta:
        verbose_name = _('История статусов заявки от зависимого')
        verbose_name_plural = _('История статусов заявок от зависимых')
        ordering = ['-changed_at']

    def __str__(self):
        return f'{self.request.get_full_name()} - {self.old_status} -> {self.new_status}'

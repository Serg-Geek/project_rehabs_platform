from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from facilities.models import MedicalFacility
from medical_services.models import Service

class AnonymousRequest(TimeStampedModel):
    """
    Анонимные заявки от пользователей
    """
    class RequestType(models.TextChoices):
        CONSULTATION = 'consultation', _('Консультация')
        TREATMENT = 'treatment', _('Лечение')
        REHABILITATION = 'rehabilitation', _('Реабилитация')
        QUESTION = 'question', _('Вопрос')
        OTHER = 'other', _('Другое')

    class Status(models.TextChoices):
        NEW = 'new', _('Новая')
        IN_PROGRESS = 'in_progress', _('В обработке')
        WAITING = 'waiting', _('Ожидает ответа')
        COMPLETED = 'completed', _('Завершена')
        CANCELLED = 'cancelled', _('Отменена')

    request_type = models.CharField(
        max_length=20,
        choices=RequestType.choices,
        verbose_name=_('Тип обращения')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Имя')
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
    message = models.TextField(
        verbose_name=_('Сообщение')
    )
    patient_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Имя пациента')
    )
    patient_age = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Возраст пациента')
    )
    preferred_contact_time = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Предпочтительное время для связи')
    )
    preferred_facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='requests',
        verbose_name=_('Предпочтительное учреждение')
    )
    preferred_service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='requests',
        verbose_name=_('Предпочтительная услуга')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_('Статус')
    )

    class Meta:
        verbose_name = _('Анонимная заявка')
        verbose_name_plural = _('Анонимные заявки')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_request_type_display()}"

    def save(self, *args, **kwargs):
        if self.id:
            old_instance = AnonymousRequest.objects.get(id=self.id)
            if old_instance.status != self.status:
                RequestStatusHistory.objects.create(
                    request=self,
                    old_status=old_instance.status,
                    new_status=self.status
                )
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

    class Meta:
        verbose_name = _('Заметка к заявке')
        verbose_name_plural = _('Заметки к заявкам')
        ordering = ['-created_at']

    def __str__(self):
        return f"Заметка к заявке {self.request.name}"

class RequestStatusHistory(TimeStampedModel):
    """
    История изменений статуса заявки
    """
    request = models.ForeignKey(
        AnonymousRequest,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Заявка')
    )
    old_status = models.CharField(
        max_length=20,
        choices=AnonymousRequest.Status.choices,
        verbose_name=_('Старый статус')
    )
    new_status = models.CharField(
        max_length=20,
        choices=AnonymousRequest.Status.choices,
        verbose_name=_('Новый статус')
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Комментарий')
    )

    class Meta:
        verbose_name = _('История статуса')
        verbose_name_plural = _('История статусов')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request.name} - {self.get_old_status_display()} -> {self.get_new_status_display()}"

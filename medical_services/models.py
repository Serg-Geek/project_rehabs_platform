from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from staff.models import MedicalSpecialist
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ServiceCategory(TimeStampedModel):
    """
    Категории медицинских услуг
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительская категория')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )

    class Meta:
        verbose_name = _('Категория услуг')
        verbose_name_plural = _('Категории услуг')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class TherapyMethod(TimeStampedModel):
    """
    Методы терапии
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )

    class Meta:
        verbose_name = _('Метод терапии')
        verbose_name_plural = _('Методы терапии')
        ordering = ['name']

    def __str__(self):
        return self.name

class Service(TimeStampedModel):
    """
    Медицинские услуги
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name=_('Категория')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    duration = models.PositiveIntegerField(
        help_text=_('Длительность в минутах'),
        verbose_name=_('Длительность')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )

    class Meta:
        verbose_name = _('Услуга')
        verbose_name_plural = _('Услуги')
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

class FacilityService(TimeStampedModel):
    """
    Услуги, предоставляемые учреждением
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Тип контента')
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта')
    )
    facility = GenericForeignKey('content_type', 'object_id')
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='facilities',
        verbose_name=_('Услуга')
    )
    specialists = models.ManyToManyField(
        MedicalSpecialist,
        related_name='facility_services',
        verbose_name=_('Специалисты')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )

    class Meta:
        verbose_name = _('Услуга учреждения')
        verbose_name_plural = _('Услуги учреждений')
        unique_together = ['content_type', 'object_id', 'service']
        ordering = ['service']

    def __str__(self):
        return f"{self.facility} - {self.service}"

class ServicePrice(TimeStampedModel):
    """
    История цен на услуги
    """
    facility_service = models.ForeignKey(
        FacilityService,
        on_delete=models.CASCADE,
        related_name='price_history',
        verbose_name=_('Услуга учреждения')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Цена')
    )
    start_date = models.DateField(
        verbose_name=_('Дата начала')
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата окончания')
    )

    class Meta:
        verbose_name = _('История цен')
        verbose_name_plural = _('История цен')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.facility_service} - {self.price} ({self.start_date})"

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from core.models import TimeStampedModel
from core.utils import generate_slug
from staff.models import MedicalSpecialist
from facilities.models import RehabCenter
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
        verbose_name=_('Slug'),
        blank=True
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Meta Title')
    )
    meta_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Meta Description')
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
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )

    class Meta:
        verbose_name = _('Категория услуг')
        verbose_name_plural = _('Категории услуг')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, ServiceCategory, self)
        super().save(*args, **kwargs)

    def active_services(self):
        """
        Получить только активные услуги категории.
        
        Returns:
            QuerySet: Активные услуги категории
        """
        return self.services.filter(is_active=True).order_by('-display_priority', 'name')

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
        verbose_name=_('Slug'),
        blank=True
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Meta Title')
    )
    meta_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Meta Description')
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
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, TherapyMethod, self)
        super().save(*args, **kwargs)

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
        verbose_name=_('Slug'),
        blank=True
    )
    categories = models.ManyToManyField(
        ServiceCategory,
        related_name='services',
        verbose_name=_('Категории')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Meta Title')
    )
    meta_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Meta Description')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна')
    )
    is_rehabilitation_program = models.BooleanField(
        default=False,
        verbose_name='Реабилитационная программа',
        help_text='Отметьте, если услуга является реабилитационной программой'
    )
    PRIORITY_HIGH = 3
    PRIORITY_MEDIUM = 2
    PRIORITY_LOW = 1
    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, 'Высокий'),
        (PRIORITY_MEDIUM, 'Средний'),
        (PRIORITY_LOW, 'Низкий'),
    ]
    display_priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name='Приоритет отображения',
        help_text='Высокий — 3, Средний — 2, Низкий — 1'
    )

    class Meta:
        verbose_name = _('Услуга')
        verbose_name_plural = _('Услуги')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, Service, self)
        super().save(*args, **kwargs)

class FacilityService(TimeStampedModel):
    """
    Услуги, предоставляемые учреждением
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Тип учреждения')
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID учреждения')
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
        verbose_name=_('Специалисты'),
        blank=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_('Цена'),
        null=True,
        blank=True
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
        'FacilityService',
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

@receiver(post_save, sender='medical_services.FacilityService')
def update_price_history(sender, instance, created, **kwargs):
    """
    Автоматически обновляет историю цен при изменении цены услуги
    """
    if created and instance.price:
        # Для новой услуги создаем первую запись в истории
        ServicePrice.objects.create(
            facility_service=instance,
            price=instance.price,
            start_date=timezone.now().date()
        )
    elif not created and instance.price:
        # Для существующей услуги проверяем последнюю цену
        last_price = ServicePrice.objects.filter(
            facility_service=instance,
            end_date__isnull=True
        ).first()

        if not last_price or last_price.price != instance.price:
            # Если цена изменилась, закрываем старую запись и создаем новую
            if last_price:
                last_price.end_date = timezone.now().date()
                last_price.save()

            ServicePrice.objects.create(
                facility_service=instance,
                price=instance.price,
                start_date=timezone.now().date()
            )

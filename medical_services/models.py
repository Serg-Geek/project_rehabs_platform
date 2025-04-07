from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from core.models import TimeStampedModel
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
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

@receiver(pre_save, sender=FacilityService)
def update_price_history(sender, instance, **kwargs):
    """
    Автоматически обновляет историю цен при изменении цены услуги
    """
    if not instance.pk:  # Новый объект
        if instance.price:
            ServicePrice.objects.create(
                facility_service=instance,
                price=instance.price,
                start_date=timezone.now().date()
            )
    else:  # Существующий объект
        old_instance = FacilityService.objects.get(pk=instance.pk)
        if old_instance.price != instance.price:
            # Закрываем предыдущую запись в истории
            ServicePrice.objects.filter(
                facility_service=instance,
                end_date__isnull=True
            ).update(end_date=timezone.now().date())
            
            # Создаем новую запись, если цена установлена
            if instance.price:
                ServicePrice.objects.create(
                    facility_service=instance,
                    price=instance.price,
                    start_date=timezone.now().date()
                )

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

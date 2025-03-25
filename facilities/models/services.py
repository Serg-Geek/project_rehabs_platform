# facilities/models/services.py
from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class ServiceCategory(models.Model):
    """Категории услуг (терапия, диагностика и т.д.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=30, blank=True)  # Иконка из UI-кита

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"
        ordering = ['name']

class Service(models.Model):
    """Базовая модель медицинской услуги"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='services'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name if self.category else 'без категории'})"

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ['category__name', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

class ServiceProvider(models.Model):
    """
    Абстрактная модель для связи услуг с провайдерами
    (Наследуется конкретными моделями InstitutionService/DoctorService)
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='%(class)s_related'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField(
        help_text="Длительность оказания услуги"
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        abstract = True

class InstitutionService(ServiceProvider):
    """Услуги, предоставляемые медицинскими учреждениями"""
    institution = models.ForeignKey(
        'facilities.MedicalInstitution',
        on_delete=models.CASCADE,
        related_name='services'# Доступ: medical_institution.services.all()
    )

    class Meta:
        unique_together = ('institution', 'service')
        verbose_name = "Услуга учреждения"
        verbose_name_plural = "Услуги учреждений"

    def __str__(self):
        return f"{self.institution.name}: {self.service.name}"

class DoctorService(ServiceProvider):
    """Услуги частных врачей"""
    doctor = models.ForeignKey(
        'facilities.PrivateDoctor',
        on_delete=models.CASCADE,
        related_name='services'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Основная специализация"
    )

    class Meta:
        unique_together = ('doctor', 'service')
        verbose_name = "Услуга врача"
        verbose_name_plural = "Услуги врачей"

    def __str__(self):
        return f"{self.doctor.full_name}: {self.service.name}"

class PriceHistory(models.Model):
    """История изменения цен"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "История цены"
        verbose_name_plural = "История цен"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.content_object}: {self.old_price}→{self.new_price}"
    
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel, City

class OrganizationType(TimeStampedModel):
    """
    Тип организации (клиника, реабилитационный центр)
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
        verbose_name=_('Описание')
    )
    competencies = models.TextField(
        verbose_name=_('Ключевые компетенции')
    )

    class Meta:
        verbose_name = _('Тип организации')
        verbose_name_plural = _('Типы организаций')
        ordering = ['name']

    def __str__(self):
        return self.name

class MedicalFacility(TimeStampedModel):
    """
    Базовая модель для всех медицинских учреждений
    """
    name = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    organization_type = models.ForeignKey(
        OrganizationType,
        on_delete=models.PROTECT,
        verbose_name=_('Тип организации')
    )
    description = models.TextField(
        verbose_name=_('Описание')
    )
    address = models.TextField(
        verbose_name=_('Адрес')
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Телефон')
    )
    email = models.EmailField(
        verbose_name=_('Email')
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Веб-сайт')
    )
    license_number = models.CharField(
        max_length=50,
        verbose_name=_('Номер лицензии')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активно')
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        verbose_name=_('Город')
    )

    class Meta:
        verbose_name = _('Медицинское учреждение')
        verbose_name_plural = _('Медицинские учреждения')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.organization_type.name})"

class Clinic(MedicalFacility):
    """
    Модель клиники с специфическими полями
    """
    emergency_support = models.BooleanField(
        default=False,
        verbose_name=_('Экстренная помощь')
    )
    has_hospital = models.BooleanField(
        default=False,
        verbose_name=_('Стационар')
    )

    class Meta:
        verbose_name = _('Клиника')
        verbose_name_plural = _('Клиники')

class RehabCenter(MedicalFacility):
    """
    Модель реабилитационного центра с специфическими полями
    """
    capacity = models.IntegerField(
        verbose_name=_('Вместимость')
    )
    program_duration = models.IntegerField(
        verbose_name=_('Длительность программы (дней)')
    )
    accommodation_conditions = models.TextField(
        verbose_name=_('Условия проживания')
    )

    class Meta:
        verbose_name = _('Реабилитационный центр')
        verbose_name_plural = _('Реабилитационные центры')

class Review(TimeStampedModel):
    """
    Модель отзыва о медицинском учреждении
    """
    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Учреждение')
    )
    rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name=_('Оценка')
    )
    content = models.TextField(
        verbose_name=_('Содержание отзыва')
    )

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв о {self.facility.name} ({self.rating} звезд)"

class FacilityImage(TimeStampedModel):
    """
    Фотографии медицинских учреждений
    """
    class ImageType(models.TextChoices):
        MAIN = 'main', _('Главное фото')
        EXTERIOR = 'exterior', _('Экстерьер')
        INTERIOR = 'interior', _('Интерьер')
        EQUIPMENT = 'equipment', _('Оборудование')
        OTHER = 'other', _('Другое')

    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Учреждение')
    )
    image = models.ImageField(
        upload_to='facilities/',
        verbose_name=_('Изображение')
    )
    image_type = models.CharField(
        max_length=20,
        choices=ImageType.choices,
        verbose_name=_('Тип изображения')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание')
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name=_('Главное фото')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )

    class Meta:
        verbose_name = _('Фото учреждения')
        verbose_name_plural = _('Фото учреждений')
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.facility.name} - {self.get_image_type_display()}"

class FacilityDocument(TimeStampedModel):
    """
    Документы медицинских учреждений
    """
    class DocumentType(models.TextChoices):
        LICENSE = 'license', _('Лицензия')
        CERTIFICATE = 'certificate', _('Сертификат')
        ACCREDITATION = 'accreditation', _('Аккредитация')
        INSURANCE = 'insurance', _('Страховка')
        OTHER = 'other', _('Другое')

    facility = models.ForeignKey(
        MedicalFacility,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Учреждение')
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        verbose_name=_('Тип документа')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    document = models.FileField(
        upload_to='facilities/documents/',
        verbose_name=_('Документ')
    )
    number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Номер документа')
    )
    issue_date = models.DateField(
        verbose_name=_('Дата выдачи')
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Срок действия')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )

    class Meta:
        verbose_name = _('Документ учреждения')
        verbose_name_plural = _('Документы учреждений')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.facility.name} - {self.get_document_type_display()}"

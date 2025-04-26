from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel, City
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models import Q

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

class AbstractMedicalFacility(TimeStampedModel):
    """
    Абстрактная базовая модель для всех медицинских учреждений
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
        verbose_name=_('Описание'),
        default=''
    )
    address = models.TextField(
        verbose_name=_('Адрес'),
        default=''
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Телефон'),
        default=''
    )
    email = models.EmailField(
        verbose_name=_('Email'),
        default='',
        blank=True,
        null=True
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Веб-сайт')
    )
    license_number = models.CharField(
        max_length=50,
        verbose_name=_('Номер лицензии'),
        default='',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активно')
    )
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        verbose_name=_('Город'),
        null=True,
        blank=True
    )

    class Meta:
        abstract = True
        verbose_name = _('Медицинское учреждение')
        verbose_name_plural = _('Медицинские учреждения')
        ordering = ['name']

    def get_absolute_url(self):
        """Получить абсолютный URL учреждения"""
        if isinstance(self, RehabCenter):
            return reverse('facilities:rehab_detail', kwargs={'slug': self.slug})
        elif isinstance(self, Clinic):
            return reverse('facilities:clinic_detail', kwargs={'slug': self.slug})
        return '#'  # Fallback URL

    def __str__(self):
        return f"{self.name} ({self.organization_type.name}) [ID: {self.id}]"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Формируем базовый слаг из названия
            base_slug = slugify(self.name)
            slug = base_slug
            
            # Проверяем, существует ли уже такой слаг
            counter = 1
            while self.__class__.objects.filter(Q(slug=slug) & ~Q(pk=self.pk)).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)

class Clinic(AbstractMedicalFacility):
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
    specialists = GenericRelation(
        'staff.FacilitySpecialist',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='clinic',
        verbose_name=_('Специалисты')
    )
    images = GenericRelation(
        'FacilityImage',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='clinic',
        verbose_name=_('Изображения')
    )
    documents = GenericRelation(
        'FacilityDocument',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='clinic',
        verbose_name=_('Документы')
    )
    reviews = GenericRelation(
        'reviews.Review',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='facility',
        verbose_name=_('Отзывы')
    )

    class Meta:
        verbose_name = _('Клиника')
        verbose_name_plural = _('Клиники')

class RehabCenter(AbstractMedicalFacility):
    """
    Модель реабилитационного центра с специфическими полями
    """
    capacity = models.IntegerField(
        verbose_name=_('Вместимость'),
        default=0
    )
    program_duration = models.IntegerField(
        verbose_name=_('Длительность программы (дней)'),
        default=0
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Минимальная цена'),
        default=0
    )
    accommodation_conditions = models.TextField(
        verbose_name=_('Условия проживания'),
        default='',
        blank=True,
        null=True
    )
    specialists = GenericRelation(
        'staff.FacilitySpecialist',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='rehab_center',
        verbose_name=_('Специалисты')
    )
    images = GenericRelation(
        'FacilityImage',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='rehab_center',
        verbose_name=_('Изображения')
    )
    documents = GenericRelation(
        'FacilityDocument',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='rehab_center',
        verbose_name=_('Документы')
    )
    reviews = GenericRelation(
        'reviews.Review',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='facility',
        verbose_name=_('Отзывы')
    )
    address = models.TextField(
        verbose_name=_('Адрес'),
        default=''
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_('Телефон'),
        default=''
    )
    email = models.EmailField(
        verbose_name=_('Email'),
        default='',
        blank=True,
        null=True
    )
    license_number = None  # Переопределяем поле, чтобы оно не отображалось в админке

    class Meta:
        verbose_name = _('Реабилитационный центр')
        verbose_name_plural = _('Реабилитационные центры')

class Review(TimeStampedModel):
    """
    Модель отзыва о медицинском учреждении
    """
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        verbose_name=_('Тип контента')
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта')
    )
    facility = GenericForeignKey('content_type', 'object_id')
    
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
        return f"Отзыв о {self.facility} ({self.rating} звезд)"

class FacilityImage(TimeStampedModel):
    """
    Модель для хранения изображений учреждений
    """
    class ImageType(models.TextChoices):
        MAIN = 'main', _('Главное фото')
        EXTERIOR = 'exterior', _('Экстерьер')
        INTERIOR = 'interior', _('Интерьер')
        EQUIPMENT = 'equipment', _('Оборудование')
        OTHER = 'other', _('Другое')

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Тип контента')
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта')
    )
    facility = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(
        upload_to='facilities/images/',
        verbose_name=_('Изображение')
    )
    image_type = models.CharField(
        max_length=50,
        choices=ImageType.choices,
        default=ImageType.MAIN,
        verbose_name=_('Тип изображения')
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Название')
    )
    description = models.TextField(
        blank=True,
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
        verbose_name = _('Изображение учреждения')
        verbose_name_plural = _('Изображения учреждений')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} ({self.image_type})"

    def to_dict(self):
        return {
            'id': self.id,
            'image': self.image.url if self.image else None,
            'image_type': self.image_type,
            'title': self.title,
            'description': self.description,
            'is_main': self.is_main,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

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

    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        verbose_name=_('Тип контента')
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта')
    )
    facility = GenericForeignKey('content_type', 'object_id')
    
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
        return f"{self.facility} - {self.get_document_type_display()}"

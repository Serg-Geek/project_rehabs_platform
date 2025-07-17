from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models import Q
from django.urls import reverse
from reviews.models import Review
from core.utils import transliterate, generate_slug

class Specialization(TimeStampedModel):
    """
    Специализации медицинских работников
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
        verbose_name=_('Описание')
    )

    class Meta:
        verbose_name = _('Специализация')
        verbose_name_plural = _('Специализации')
        ordering = ['name']

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name, Specialization, self)
        super().save(*args, **kwargs)

class MedicalSpecialist(TimeStampedModel):
    """
    Базовая модель для всех медицинских специалистов
    """
    first_name = models.CharField(
        max_length=100,
        verbose_name=_('Имя')
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name=_('Фамилия')
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Отчество')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug'),
        blank=True
    )
    specializations = models.ManyToManyField(
        Specialization,
        verbose_name=_('Специализации')
    )
    experience_years = models.IntegerField(
        verbose_name=_('Стаж (лет)')
    )
    education = models.TextField(
        verbose_name=_('Образование')
    )
    biography = models.TextField(
        verbose_name=_('Биография'),
        blank=True,
        null=True
    )
    achievements = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Достижения')
    )
    photo = models.ImageField(
        upload_to='specialists/',
        blank=True,
        null=True,
        verbose_name=_('Фото')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )

    reviews = GenericRelation(
        'reviews.Review',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='specialist',
        verbose_name=_('Отзывы')
    )

    class Meta:
        verbose_name = _('Медицинский специалист')
        verbose_name_plural = _('Медицинские специалисты')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_full_name(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"
        
    def save(self, *args, **kwargs):
        if not self.slug or self.slug.startswith('-'):
            # Формируем базовый слаг из фамилии и имени
            base_slug = slugify(f"{self.last_name}-{self.first_name}")
            if not base_slug:  # Если после slugify получили пустую строку
                base_slug = f"specialist-{self.id}" if self.id else "specialist"
            slug = base_slug
            
            # Проверяем, существует ли уже такой слаг
            counter = 1
            while MedicalSpecialist.objects.filter(Q(slug=slug) & ~Q(pk=self.pk)).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)

class FacilitySpecialist(MedicalSpecialist):
    """
    Специалист, работающий в медицинском учреждении
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Тип контента'),
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта'),
        null=True,
        blank=True
    )
    facility = GenericForeignKey('content_type', 'object_id')
    
    position = models.CharField(
        max_length=100,
        verbose_name=_('Должность'),
        blank=True,
        null=True
    )
    schedule = models.TextField(
        verbose_name=_('График работы'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Специалист учреждения')
        verbose_name_plural = _('Специалисты учреждений')

    def save(self, *args, **kwargs):
        if not self.content_type or not self.object_id:
            raise ValueError("Facility specialist must be associated with a facility")
        # Вызываем save() родительского класса для генерации slug
        super(FacilitySpecialist, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('staff:specialist_detail', kwargs={'slug': self.slug})

class SpecialistDocument(TimeStampedModel):
    """
    Документы специалистов
    """
    class DocumentType(models.TextChoices):
        DIPLOMA = 'diploma', _('Диплом')
        CERTIFICATE = 'certificate', _('Сертификат')
        LICENSE = 'license', _('Лицензия')
        SPECIALIZATION = 'specialization', _('Специализация')
        OTHER = 'other', _('Другое')

    specialist = models.ForeignKey(
        MedicalSpecialist,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('Специалист')
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
        upload_to='specialists/documents/',
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
        verbose_name = _('Документ специалиста')
        verbose_name_plural = _('Документы специалистов')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.specialist} - {self.get_document_type_display()}"

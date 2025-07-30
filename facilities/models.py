from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel, City
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.db.models import Q
from .managers import FacilityManager, ClinicManager, RehabCenterManager, PrivateDoctorManager

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
        """
        String representation of the organization type.
        
        Returns:
            str: Organization type name
        """
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
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Показать на главной странице'),
        help_text=_('Отметьте, чтобы показать учреждение на главной странице в приоритетном порядке')
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
        """
        Get the absolute URL for the facility.
        
        Returns:
            str: URL for the facility's detail page
        """
        if isinstance(self, RehabCenter):
            return reverse('facilities:rehab_detail', kwargs={'slug': self.slug})
        elif isinstance(self, Clinic):
            return reverse('facilities:clinic_detail', kwargs={'slug': self.slug})
        elif isinstance(self, PrivateDoctor):
            return reverse('facilities:private_doctor_detail', kwargs={'slug': self.slug})
        return '#'  # Fallback URL

    def __str__(self):
        """
        String representation of the medical facility.
        
        Returns:
            str: Facility name with organization type and ID
        """
        return f"{self.name} ({self.organization_type.name}) [ID: {self.id}]"

    def save(self, *args, **kwargs):
        """
        Save the facility with automatic slug generation.
        
        If slug is not provided, generates it from the facility name.
        Handles slug duplication by adding numeric suffix.
        """
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
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Meta Keywords')
    )
    meta_image = models.ImageField(
        upload_to='facilities/meta_images/',
        blank=True,
        null=True,
        verbose_name=_('Meta Image (OG/Twitter)')
    )
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

    # Используем кастомный manager
    objects = ClinicManager()

    def active_specialists(self):
        """
        Получить только активных специалистов учреждения.
        
        Returns:
            QuerySet: Активные специалисты учреждения
        """
        from staff.models import FacilitySpecialist
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(self)
        return FacilitySpecialist.objects.filter(
            content_type=ct,
            object_id=self.pk,
            is_active=True
        ).order_by('last_name', 'first_name')

    class Meta:
        verbose_name = _('Клиника')
        verbose_name_plural = _('Клиники')

class RehabCenter(AbstractMedicalFacility):
    """
    Модель реабилитационного центра с специфическими полями
    """
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
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Meta Keywords')
    )
    meta_image = models.ImageField(
        upload_to='facilities/meta_images/',
        blank=True,
        null=True,
        verbose_name=_('Meta Image (OG/Twitter)')
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

    # Используем кастомный manager
    objects = RehabCenterManager()

    def active_specialists(self):
        """
        Получить только активных специалистов учреждения.
        
        Returns:
            QuerySet: Активные специалисты учреждения
        """
        from staff.models import FacilitySpecialist
        from django.contrib.contenttypes.models import ContentType
        
        ct = ContentType.objects.get_for_model(self)
        return FacilitySpecialist.objects.filter(
            content_type=ct,
            object_id=self.pk,
            is_active=True
        ).order_by('last_name', 'first_name')

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
        """
        String representation of the review.
        
        Returns:
            str: Review content with truncation
        """
        return self.content[:100] + '...' if len(self.content) > 100 else self.content

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
        """
        String representation of the image.
        
        Returns:
            str: Image title or image type
        """
        return self.title or f"Изображение {self.get_image_type_display()}"

    def to_dict(self):
        """
        Convert the image to a dictionary for API responses.
        
        Returns:
            dict: Dictionary with image data
        """
        return {
            'id': self.id,
            'image': self.image.url if self.image else None,
            'image_type': self.image_type,
            'title': self.title,
            'description': self.description,
            'is_main': self.is_main,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
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
        """
        String representation of the facility document.
        
        Returns:
            str: Document title with document type
        """
        return f"{self.title} ({self.get_document_type_display()})"

class PrivateDoctor(AbstractMedicalFacility):
    """
    Модель частнопрактикующего врача
    """
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
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Meta Keywords')
    )
    meta_image = models.ImageField(
        upload_to='facilities/meta_images/',
        blank=True,
        null=True,
        verbose_name=_('Meta Image (OG/Twitter)')
    )
    # Персональная информация
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
    specializations = models.ManyToManyField(
        'staff.Specialization',
        verbose_name=_('Специализации')
    )
    experience_years = models.IntegerField(
        verbose_name=_('Стаж (лет)')
    )
    education = models.TextField(
        verbose_name=_('Образование'),
        blank=True,
        null=True
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
    
    # Место приема
    office_description = models.TextField(
        verbose_name=_('Описание кабинета/офиса'),
        blank=True,
        null=True
    )
    parking_available = models.BooleanField(
        default=False,
        verbose_name=_('Наличие парковки')
    )
    wheelchair_accessible = models.BooleanField(
        default=False,
        verbose_name=_('Доступность для инвалидных колясок')
    )
    
    # График работы
    schedule = models.TextField(
        verbose_name=_('График работы')
    )
    home_visits = models.BooleanField(
        default=False,
        verbose_name=_('Выезд на дом')
    )
    emergency_available = models.BooleanField(
        default=False,
        verbose_name=_('Экстренная помощь')
    )
    weekend_work = models.BooleanField(
        default=False,
        verbose_name=_('Работа в выходные')
    )
    
    # Финансовые аспекты
    consultation_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Стоимость консультации'),
        null=True,
        blank=True
    )
    home_visit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Стоимость выезда на дом'),
        null=True,
        blank=True
    )
    insurance_accepted = models.BooleanField(
        default=False,
        verbose_name=_('Принимает страховку')
    )
    
    # Лицензирование
    license_issue_date = models.DateField(
        verbose_name=_('Дата выдачи лицензии'),
        null=True,
        blank=True
    )
    license_expiry_date = models.DateField(
        verbose_name=_('Срок действия лицензии'),
        null=True,
        blank=True
    )
    
    # Дополнительные возможности
    online_consultations = models.BooleanField(
        default=False,
        verbose_name=_('Онлайн консультации')
    )
    video_consultations = models.BooleanField(
        default=False,
        verbose_name=_('Видеоконсультации')
    )
    special_equipment = models.TextField(
        verbose_name=_('Специальное оборудование'),
        blank=True,
        null=True
    )
    
    # Generic Relations
    specialists = GenericRelation(
        'staff.FacilitySpecialist',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='private_doctor',
        verbose_name=_('Специалисты')
    )
    images = GenericRelation(
        'FacilityImage',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='private_doctor',
        verbose_name=_('Изображения')
    )
    documents = GenericRelation(
        'FacilityDocument',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='private_doctor',
        verbose_name=_('Документы')
    )
    reviews = GenericRelation(
        'reviews.Review',
        content_type_field='content_type',
        object_id_field='object_id',
        related_query_name='facility',
        verbose_name=_('Отзывы')
    )

    # Используем кастомный manager
    objects = PrivateDoctorManager()

    class Meta:
        verbose_name = _('Частный врач')
        verbose_name_plural = _('Частные врачи')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        """
        String representation of the private doctor.
        
        Returns:
            str: Full name with organization type and ID
        """
        return f"{self.get_full_name()} ({self.organization_type.name}) [ID: {self.id}]"

    def get_full_name(self):
        """
        Get the full name of the doctor.
        
        Returns:
            str: Full name including middle name if available
        """
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

    def get_absolute_url(self):
        """
        Get the absolute URL for the doctor's detail page.
        
        Returns:
            str: URL for the doctor's detail page
        """
        return reverse('facilities:private_doctor_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        Save the doctor with automatic name and slug generation.
        
        If name is not provided, generates it from first and last name.
        If slug is not provided, generates it from last and first name.
        Handles slug duplication by adding numeric suffix.
        """
        # Формируем название из имени и фамилии
        if not self.name:
            self.name = self.get_full_name()
        
        # Формируем базовый слаг из фамилии и имени
        if not self.slug:
            base_slug = slugify(f"{self.last_name}-{self.first_name}")
            slug = base_slug
            
            # Проверяем, существует ли уже такой слаг
            counter = 1
            while PrivateDoctor.objects.filter(Q(slug=slug) & ~Q(pk=self.pk)).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        """
        Calculate the average rating from all reviews.
        
        Returns:
            float: Average rating (0.0 if no reviews)
        """
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    @property
    def reviews_count(self):
        """
        Get the total number of reviews.
        
        Returns:
            int: Number of reviews
        """
        return self.reviews.count()

    @property
    def main_image(self):
        """
        Get the main image of the doctor.
        
        Returns:
            FacilityImage or None: Main image (is_main=True) or first image or None
        """
        return self.images.filter(is_main=True).first() or self.images.first()

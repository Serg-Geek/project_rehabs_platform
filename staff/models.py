from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

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
        verbose_name=_('Slug')
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
        verbose_name=_('Slug')
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
        verbose_name=_('Биография')
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

class FacilitySpecialist(MedicalSpecialist):
    """
    Специалист, работающий в медицинском учреждении
    """
    facility = models.ForeignKey(
        'facilities.MedicalFacility',
        on_delete=models.CASCADE,
        verbose_name=_('Медицинское учреждение')
    )
    position = models.CharField(
        max_length=100,
        verbose_name=_('Должность')
    )
    schedule = models.TextField(
        verbose_name=_('График работы')
    )

    class Meta:
        verbose_name = _('Специалист учреждения')
        verbose_name_plural = _('Специалисты учреждений')

class PrivateSpecialist(MedicalSpecialist):
    """
    Частнопрактикующий специалист
    """
    consultation_address = models.TextField(
        verbose_name=_('Адрес приёма')
    )
    consultation_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Стоимость консультации')
    )
    available_online = models.BooleanField(
        default=False,
        verbose_name=_('Доступны онлайн-консультации')
    )
    license_number = models.CharField(
        max_length=50,
        verbose_name=_('Номер лицензии')
    )
    regions_of_work = models.ManyToManyField(
        'core.Region',
        verbose_name=_('Регионы работы')
    )

    class Meta:
        verbose_name = _('Частный специалист')
        verbose_name_plural = _('Частные специалисты')

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

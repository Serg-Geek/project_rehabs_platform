from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

class User(AbstractUser):
    """
    Расширенная модель пользователя
    """
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    email = models.EmailField(
        _('email address'),
        unique=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон')
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.email

class UserProfile(TimeStampedModel):
    """
    Профиль пользователя с дополнительной информацией
    """
    class Gender(models.TextChoices):
        MALE = 'male', _('Мужской')
        FEMALE = 'female', _('Женский')
        OTHER = 'other', _('Другой')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Пользователь')
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Дата рождения')
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        null=True,
        verbose_name=_('Пол')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Адрес')
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('О себе')
    )
    notification_preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Настройки уведомлений')
    )

    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')

    def __str__(self):
        return f"Профиль {self.user.email}"

class PatientProfile(TimeStampedModel):
    """
    Профиль пациента с медицинской информацией
    """
    class BloodType(models.TextChoices):
        A_POSITIVE = 'A+', _('A+')
        A_NEGATIVE = 'A-', _('A-')
        B_POSITIVE = 'B+', _('B+')
        B_NEGATIVE = 'B-', _('B-')
        AB_POSITIVE = 'AB+', _('AB+')
        AB_NEGATIVE = 'AB-', _('AB-')
        O_POSITIVE = 'O+', _('O+')
        O_NEGATIVE = 'O-', _('O-')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        verbose_name=_('Пользователь')
    )
    medical_record_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Номер медицинской карты')
    )
    blood_type = models.CharField(
        max_length=3,
        choices=BloodType.choices,
        blank=True,
        null=True,
        verbose_name=_('Группа крови')
    )
    allergies = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Аллергии')
    )
    chronic_diseases = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Хронические заболевания')
    )
    current_medications = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Текущие медикаменты')
    )
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Контактное лицо для экстренных случаев')
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Телефон для экстренных случаев')
    )
    insurance_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Информация о страховке')
    )

    class Meta:
        verbose_name = _('Профиль пациента')
        verbose_name_plural = _('Профили пациентов')

    def __str__(self):
        return f"Пациент {self.user.email}"

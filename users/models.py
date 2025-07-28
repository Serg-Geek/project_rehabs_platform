from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta

class UserManager(BaseUserManager):
    """
    Custom user manager for creating users and superusers.
    """
    
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and save a regular user.
        
        Args:
            username: Username for the user
            email: Email address (required)
            password: Password for the user
            **extra_fields: Additional fields for the user
            
        Returns:
            User: Created user instance
            
        Raises:
            ValueError: If email or username is not provided
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and save a superuser.
        
        Args:
            username: Username for the superuser
            email: Email address (required)
            password: Password for the superuser
            **extra_fields: Additional fields for the superuser
            
        Returns:
            User: Created superuser instance
            
        Raises:
            ValueError: If required superuser fields are not set correctly
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superuser')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        if extra_fields.get('role') != 'superuser':
            extra_fields['role'] = 'superuser'

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    """
    Модель пользователя
    """
    class Role(models.TextChoices):
        SUPERUSER = 'superuser', _('Суперпользователь')
        CONTENT_ADMIN = 'content_admin', _('Администратор контента')
        REQUESTS_ADMIN = 'requests_admin', _('Администратор заявок')
        USER = 'user', _('Пользователь')

    role = models.CharField(
        _('Роль'),
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    email = models.EmailField(
        _('Email'),
        unique=True
    )
    is_active = models.BooleanField(
        _('Активен'),
        default=True
    )
    last_login = models.DateTimeField(
        _('Последний вход'),
        null=True,
        blank=True
    )
    date_joined = models.DateTimeField(
        _('Дата регистрации'),
        auto_now_add=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        """
        String representation of the user.
        
        Returns:
            str: Full name or username
        """
        return self.get_full_name() or self.username

    def has_role(self, role):
        """
        Check if user has a specific role.
        
        Args:
            role: Role to check
            
        Returns:
            bool: True if user has the specified role
        """
        return self.role == role

    def is_content_admin(self):
        """
        Check if user is a content administrator.
        
        Returns:
            bool: True if user is superuser or content admin
        """
        return self.role in [self.Role.SUPERUSER, self.Role.CONTENT_ADMIN]

    def is_requests_admin(self):
        """
        Check if user is a requests administrator.
        
        Returns:
            bool: True if user is superuser or requests admin
        """
        return self.role in [self.Role.SUPERUSER, self.Role.REQUESTS_ADMIN]

    def save(self, *args, **kwargs):
        """
        Override save method to hash password if needed.
        
        Automatically hashes plain text passwords when creating new users.
        """
        if self._state.adding and self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class UserProfile(TimeStampedModel):
    """
    Профиль пользователя с дополнительной информацией
    """
    class Gender(models.TextChoices):
        MALE = 'male', _('Мужской')
        FEMALE = 'female', _('Женский')

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

    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')

    def __str__(self):
        """
        String representation of the user profile.
        
        Returns:
            str: Profile description with user email
        """
        return f"Профиль {self.user.email}"

class UserActionLog(TimeStampedModel):
    """
    Model for logging user actions.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='action_logs',
        verbose_name=_('Пользователь')
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('create', _('Создание')),
            ('update', _('Обновление')),
            ('delete', _('Удаление')),
        ],
        verbose_name=_('Действие')
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name=_('Модель')
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта')
    )
    details = models.TextField(
        verbose_name=_('Детали')
    )

    class Meta:
        verbose_name = _('Лог действий пользователя')
        verbose_name_plural = _('Логи действий пользователей')
        ordering = ['-created_at']

    def __str__(self):
        """
        String representation of the user action log.
        
        Returns:
            str: Action description with user and model
        """
        return f"{self.user} - {self.action} - {self.model_name}"

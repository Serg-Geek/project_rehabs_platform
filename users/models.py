from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from django.utils import timezone
from django.contrib.auth.hashers import make_password

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
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
    Расширенная модель пользователя
    """
    class Role(models.TextChoices):
        SUPERUSER = 'superuser', _('Суперпользователь')
        CONTENT_ADMIN = 'content_admin', _('Администратор контента')
        REQUESTS_ADMIN = 'requests_admin', _('Администратор заявок')

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
    email = models.EmailField(_('Email'), unique=True)
    phone = models.CharField(_('Телефон'), max_length=20, blank=True, null=True)
    avatar = models.ImageField(_('Аватар'), upload_to='avatars/', blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONTENT_ADMIN,
        verbose_name=_('Роль')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.get_full_name() or self.username

    def has_role(self, role):
        """Проверка роли пользователя"""
        return self.role == role

    def is_content_admin(self):
        """Проверка является ли пользователь администратором контента"""
        return self.role in [self.Role.SUPERUSER, self.Role.CONTENT_ADMIN]

    def is_requests_admin(self):
        """Проверка является ли пользователь администратором заявок"""
        return self.role in [self.Role.SUPERUSER, self.Role.REQUESTS_ADMIN]

    def save(self, *args, **kwargs):
        # Если это новый пользователь (еще не сохранен в БД)
        if not self.pk:
            # Если роль суперпользователя, устанавливаем все права
            if self.role == self.Role.SUPERUSER:
                self.is_staff = True
                self.is_superuser = True
            # Для других ролей устанавливаем только staff
            elif self.role in [self.Role.CONTENT_ADMIN, self.Role.REQUESTS_ADMIN]:
                self.is_staff = True
                self.is_superuser = False
        else:
            # Для существующего пользователя обновляем права в зависимости от роли
            if self.role == self.Role.SUPERUSER:
                self.is_staff = True
                self.is_superuser = True
            elif self.role in [self.Role.CONTENT_ADMIN, self.Role.REQUESTS_ADMIN]:
                self.is_staff = True
                self.is_superuser = False
            else:
                self.is_staff = False
                self.is_superuser = False

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
        return f"Профиль {self.user.email}"

class UserActionLog(TimeStampedModel):
    """
    Модель для логирования действий пользователей
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
        return f"{self.user.username} - {self.action} - {self.model_name} #{self.object_id}"

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

class Review(models.Model):
    """Модель отзыва"""
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Тип объекта'),
        related_name='reviews_review'
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_('ID объекта')
    )
    facility = GenericForeignKey('content_type', 'object_id')
    
    # Администратор, создавший отзыв
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_reviews',
        verbose_name=_('Кто добавил')
    )
    
    # Информация об авторе отзыва (клиенте)
    author_name = models.CharField(
        max_length=100,
        verbose_name=_('Имя автора')
    )
    author_age = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Возраст автора')
    )
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Оценка')
    )
    content = models.TextField(
        verbose_name=_('Текст отзыва')
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('Дата обновления')
    )
    is_published = models.BooleanField(
        default=True, 
        verbose_name=_('Опубликовано')
    )

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.author_name} о {self.facility}'
        
    @property
    def author_display(self):
        """Отображаемое имя автора с возрастом"""
        if self.author_age:
            return f"{self.author_name}, {self.author_age} лет"
        return self.author_name

from django.db import models
from django.utils.translation import gettext_lazy as _

class TimeStampedModel(models.Model):
    """
    Абстрактная модель с полями для отслеживания создания/изменения
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )

    class Meta:
        abstract = True

class Region(TimeStampedModel):
    """
    Модель региона
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )

    class Meta:
        verbose_name = _('Регион')
        verbose_name_plural = _('Регионы')
        ordering = ['name']

    def __str__(self):
        return self.name

class City(TimeStampedModel):
    """
    Модель города
    """
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name=_('Регион')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        verbose_name=_('Slug')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )

    class Meta:
        verbose_name = _('Город')
        verbose_name_plural = _('Города')
        ordering = ['name']
        unique_together = ['region', 'slug']

    def __str__(self):
        return f"{self.name}, {self.region.name}"

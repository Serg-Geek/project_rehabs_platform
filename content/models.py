from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Banner(models.Model):
    """Модель для баннеров на сайте"""
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    description = models.TextField(verbose_name=_('Описание'))
    image = models.ImageField(upload_to='banners/', verbose_name=_('Изображение'))
    link = models.URLField(blank=True, null=True, verbose_name=_('Ссылка'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активен'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Порядок'))
    start_date = models.DateField(verbose_name=_('Дата начала'))
    end_date = models.DateField(verbose_name=_('Дата окончания'))

    class Meta:
        verbose_name = _('Баннер')
        verbose_name_plural = _('Баннеры')
        ordering = ['order', '-start_date']

    def __str__(self):
        return self.title

    def is_current(self):
        today = timezone.now().date()
        return self.is_active and self.start_date <= today <= self.end_date

class StaticPage(models.Model):
    """Модель для статических страниц"""
    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    slug = models.SlugField(unique=True, verbose_name=_('URL'))
    content = models.TextField(verbose_name=_('Содержимое'))
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Статическая страница')
        verbose_name_plural = _('Статические страницы')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class SiteSettings(models.Model):
    """Модель для общих настроек сайта"""
    site_name = models.CharField(max_length=100, verbose_name=_('Название сайта'))
    site_description = models.TextField(verbose_name=_('Описание сайта'))
    phone = models.CharField(max_length=20, verbose_name=_('Телефон'))
    email = models.EmailField(verbose_name=_('Email'))
    address = models.TextField(verbose_name=_('Адрес'))
    working_hours = models.CharField(max_length=200, verbose_name=_('Режим работы'))
    social_media = models.JSONField(default=dict, verbose_name=_('Социальные сети'))
    seo_keywords = models.TextField(blank=True, verbose_name=_('SEO ключевые слова'))
    seo_description = models.TextField(blank=True, verbose_name=_('SEO описание'))

    class Meta:
        verbose_name = _('Настройка сайта')
        verbose_name_plural = _('Настройки сайта')

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        # Ограничиваем количество записей до одной
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Может быть только одна запись настроек сайта')
        super().save(*args, **kwargs)

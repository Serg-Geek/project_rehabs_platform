from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from django.db.models import Q
from facilities.models import RehabCenter

User = get_user_model()

class RecoveryCategory(TimeStampedModel):
    """
    Категория историй выздоровления
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
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительская категория')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )

    class Meta:
        verbose_name = _('Категория историй')
        verbose_name_plural = _('Категории историй')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class RecoveryStory(TimeStampedModel):
    """
    История выздоровления
    """
    title = models.CharField(
        max_length=200,
        verbose_name=_('Заголовок')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    category = models.ForeignKey(
        RecoveryCategory,
        on_delete=models.PROTECT,
        related_name='stories',
        verbose_name=_('Категория')
    )
    author = models.CharField(
        max_length=100,
        verbose_name=_('Автор')
    )
    rehab_center = models.ForeignKey(
        RehabCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stories',
        verbose_name=_('Реабилитационный центр')
    )
    content = models.TextField(
        verbose_name=_('Содержание')
    )
    excerpt = models.TextField(
        max_length=500,
        verbose_name=_('Краткое описание'),
        help_text=_('Краткое описание истории для отображения в списке')
    )
    image = models.ImageField(
        upload_to='recovery_stories/',
        verbose_name=_('Изображение'),
        null=True,
        blank=True
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Опубликовано')
    )
    publish_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Дата публикации')
    )
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
    views = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Просмотры')
    )
    conclusion_text = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Текст заключения')
    )
    tags = models.ManyToManyField('RecoveryTag', through='RecoveryStoryTag', verbose_name='Теги')

    class Meta:
        verbose_name = _('История выздоровления')
        verbose_name_plural = _('Истории выздоровления')
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recovery_stories:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class RecoveryStoryImage(TimeStampedModel):
    """
    Изображения для историй выздоровления
    """
    story = models.ForeignKey(
        RecoveryStory,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('История')
    )
    image = models.ImageField(
        upload_to='recovery_stories/images/',
        verbose_name=_('Изображение')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Название')
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Описание')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )

    class Meta:
        verbose_name = _('Изображение истории')
        verbose_name_plural = _('Изображения историй')
        ordering = ['order']

    def __str__(self):
        return self.title

class RecoveryTag(TimeStampedModel):
    """
    Теги для историй выздоровления
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )
    icon = models.CharField(
        max_length=100,
        verbose_name=_('Иконка'),
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name=_('Системный тег'),
        help_text=_('Системные теги отображаются с иконками в интерфейсе')
    )

    class Meta:
        verbose_name = _('Тег историй')
        verbose_name_plural = _('Теги историй')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class RecoveryStoryTag(TimeStampedModel):
    """
    Связь между историями выздоровления и тегами
    """
    story = models.ForeignKey(
        RecoveryStory,
        on_delete=models.CASCADE,
        related_name='story_tags',
        verbose_name=_('История')
    )
    tag = models.ForeignKey(
        RecoveryTag,
        on_delete=models.CASCADE,
        related_name='story_tags',
        verbose_name=_('Тег')
    )

    class Meta:
        verbose_name = _('Тег истории')
        verbose_name_plural = _('Теги историй')
        unique_together = ['story', 'tag']

    def __str__(self):
        return f"{self.story.title} - {self.tag.name}"

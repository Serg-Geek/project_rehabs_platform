from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel

class ContentCategory(TimeStampedModel):
    """
    Категория контента
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
        verbose_name = _('Категория контента')
        verbose_name_plural = _('Категории контента')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Article(TimeStampedModel):
    """
    Статья
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
        ContentCategory,
        on_delete=models.PROTECT,
        related_name='articles',
        verbose_name=_('Категория')
    )
    preview_text = models.TextField(
        verbose_name=_('Превью текст')
    )
    content = models.TextField(
        verbose_name=_('Содержание')
    )
    image = models.ImageField(
        upload_to='articles/',
        blank=True,
        null=True,
        verbose_name=_('Изображение')
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
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Количество просмотров')
    )

    class Meta:
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

class ArticleImage(TimeStampedModel):
    """
    Изображения для статей
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Статья')
    )
    image = models.ImageField(
        upload_to='articles/images/',
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
        verbose_name = _('Изображение статьи')
        verbose_name_plural = _('Изображения статей')
        ordering = ['order']

    def __str__(self):
        return f"{self.article.title} - {self.title}"

class Tag(TimeStampedModel):
    """
    Теги для статей
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Название')
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_('Slug')
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ['name']

    def __str__(self):
        return self.name

class ArticleTag(TimeStampedModel):
    """
    Связь между статьями и тегами
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='article_tags',
        verbose_name=_('Статья')
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='article_tags',
        verbose_name=_('Тег')
    )

    class Meta:
        verbose_name = _('Тег статьи')
        verbose_name_plural = _('Теги статей')
        unique_together = ['article', 'tag']

    def __str__(self):
        return f"{self.article.title} - {self.tag.name}"

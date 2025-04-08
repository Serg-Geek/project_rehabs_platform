from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel
from django.db.models import Q

User = get_user_model()

class BlogCategory(TimeStampedModel):
    """
    Категория блога
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
        verbose_name = _('Категория блога')
        verbose_name_plural = _('Категории блога')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BlogPost(TimeStampedModel):
    """
    Пост блога
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
        BlogCategory,
        on_delete=models.PROTECT,
        related_name='posts',
        verbose_name=_('Категория')
    )
    preview_text = models.TextField(
        verbose_name=_('Превью текст')
    )
    content = models.TextField(
        verbose_name=_('Содержание')
    )
    image = models.ImageField(
        upload_to='blog/',
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
    tags = models.ManyToManyField('Tag', through='BlogPostTag', verbose_name='Теги')

    class Meta:
        verbose_name = _('Пост блога')
        verbose_name_plural = _('Посты блога')
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class BlogImage(TimeStampedModel):
    """
    Изображения для постов блога
    """
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Пост')
    )
    image = models.ImageField(
        upload_to='blog/images/',
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
        verbose_name = _('Изображение поста')
        verbose_name_plural = _('Изображения постов')
        ordering = ['order']

    def __str__(self):
        return f"{self.post.title} - {self.title}"

class Tag(TimeStampedModel):
    """
    Теги для постов блога
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Создан')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Обновлен')
    )

    # Словарь с путями к иконкам для системных тегов
    SYSTEM_TAG_ICONS = {
        'profilaktika-i-preduprezhdenie': 'deps/icons/articles_tags_icons/prevention-icon.svg',
        'yuridicheskaya-konsultatsiya': 'deps/icons/articles_tags_icons/justice-hammer-icon.svg',
        'psihiatriya': 'deps/icons/articles_tags_icons/psychiatrist-icon.svg',
        'psihologiya': 'deps/icons/articles_tags_icons/psychologist-icon.svg',
        'rodstvennikam': 'deps/icons/articles_tags_icons/clients-icon.svg',
        'narkomaniya': 'deps/icons/articles_tags_icons/medicine-icon.svg',
        'alkogolizm': 'deps/icons/articles_tags_icons/alcohol-icon.svg',
    }

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_icon_path(self):
        """
        Возвращает путь к иконке для системного тега.
        Если тег не системный или иконка не найдена, возвращает None.
        """
        if not self.is_system:
            return None
        
        # Ищем иконку в словаре по слагу
        return self.SYSTEM_TAG_ICONS.get(self.slug)

class BlogPostTag(TimeStampedModel):
    """
    Связь между постами блога и тегами
    """
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='post_tags',
        verbose_name=_('Пост')
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='post_tags',
        verbose_name=_('Тег')
    )

    class Meta:
        verbose_name = _('Тег поста')
        verbose_name_plural = _('Теги постов')
        unique_together = ['post', 'tag']

    def __str__(self):
        return f"{self.post.title} - {self.tag.name}"

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
        
    def save(self, *args, **kwargs):
        if not self.slug:
            # Формируем базовый слаг из названия
            base_slug = slugify(self.name)
            slug = base_slug
            
            # Проверяем, существует ли уже такой слаг
            counter = 1
            while ContentCategory.objects.filter(Q(slug=slug) & ~Q(pk=self.pk)).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)

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
        
    def save(self, *args, **kwargs):
        if not self.slug:
            # Формируем базовый слаг из заголовка
            base_slug = slugify(self.title)
            slug = base_slug
            
            # Проверяем, существует ли уже такой слаг
            counter = 1
            while Article.objects.filter(Q(slug=slug) & ~Q(pk=self.pk)).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)

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

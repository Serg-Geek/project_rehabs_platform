from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from facilities.utils import CustomJSONEncoder
from .models import (
    BlogPost,
    BlogCategory,
    Tag,
    BlogPostTag,
    BlogImage,
    Article,
    ArticleImage,
    ContentCategory,
    ArticleTag
)


class BlogPostTagInline(admin.TabularInline):
    model = BlogPostTag
    extra = 1


class ArticleTagInline(admin.TabularInline):
    model = ArticleTag
    extra = 1


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'is_published',
        'is_featured',
        'publish_date',
        'views_count'
    ]
    list_filter = [
        'is_published',
        'is_featured',
        'category',
        'publish_date'
    ]
    search_fields = [
        'title',
        'content',
        'meta_description'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count']
    inlines = [BlogPostTagInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'slug',
                'category',
                'preview_text',
                'content',
                'conclusion_text',
            )
        }),
        ('Медиа', {
            'fields': (
                'image',
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
                'meta_image',
            ),
            'classes': ('collapse',)
        }),
        ('Публикация', {
            'fields': (
                'is_published',
                'is_featured',
                'publish_date',
                'views_count',
                'created_at',
                'updated_at',
            )
        }),
    )

    def get_json_encoder(self):
        return CustomJSONEncoder


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_system', 'is_active']
    list_filter = ['is_system', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPostTag)
class BlogPostTagAdmin(admin.ModelAdmin):
    list_display = ['post', 'tag']
    list_filter = ['tag']
    search_fields = ['post__title', 'tag__name']


@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'publish_date']
    list_filter = ['is_published', 'category', 'publish_date']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count']
    inlines = [ArticleTagInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'slug',
                'category',
                'preview_text',
                'content',
            )
        }),
        ('Медиа', {
            'fields': (
                'image',
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description',
                'meta_keywords',
                'meta_image',
            ),
            'classes': ('collapse',)
        }),
        ('Публикация', {
            'fields': (
                'is_published',
                'publish_date',
                'views_count',
                'created_at',
                'updated_at',
            )
        }),
    )

    def get_json_encoder(self):
        return CustomJSONEncoder


@admin.register(ArticleTag)
class ArticleTagAdmin(admin.ModelAdmin):
    list_display = ['article', 'tag']
    list_filter = ['tag']
    search_fields = ['article__title', 'tag__name']

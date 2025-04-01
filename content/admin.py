from django.contrib import admin
from .models import Article, ContentCategory, Tag, ArticleTag, ArticleImage

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1

class ArticleTagInline(admin.TabularInline):
    model = ArticleTag
    extra = 1

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'is_published',
        'publish_date',
        'views_count'
    ]
    list_filter = [
        'is_published',
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
    inlines = [ArticleImageInline, ArticleTagInline]
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

@admin.register(ContentCategory)
class ContentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ArticleImage)
class ArticleImageAdmin(admin.ModelAdmin):
    list_display = [
        'article',
        'title',
        'order',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['title', 'description', 'article__title']
    readonly_fields = ['created_at']

@admin.register(ArticleTag)
class ArticleTagAdmin(admin.ModelAdmin):
    list_display = [
        'article',
        'tag',
        'created_at'
    ]
    list_filter = ['tag', 'created_at']
    search_fields = ['article__title', 'tag__name']
    readonly_fields = ['created_at']

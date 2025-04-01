from django.contrib import admin
from .models import Article, ArticleCategory, Tag, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    readonly_fields = ['created_at']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'status',
        'author',
        'created_at',
        'published_at'
    ]
    list_filter = [
        'status',
        'category',
        'tags',
        'created_at',
        'published_at'
    ]
    search_fields = [
        'title',
        'content',
        'meta_description'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['tags']
    inlines = [CommentInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'slug',
                'category',
                'tags',
                'author',
            )
        }),
        ('Контент', {
            'fields': (
                'content',
                'image',
                'image_alt',
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
                'status',
                'published_at',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'article',
        'author_name',
        'is_approved',
        'created_at'
    ]
    list_filter = ['is_approved', 'created_at']
    search_fields = [
        'author_name',
        'author_email',
        'content',
        'article__title'
    ]
    readonly_fields = ['created_at']

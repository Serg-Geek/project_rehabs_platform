from django.contrib import admin
from .models import BlogCategory, BlogPost, BlogImage, Tag, BlogPostTag


class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 1


class BlogPostTagInline(admin.TabularInline):
    model = BlogPostTag
    extra = 1


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
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
    inlines = [BlogImageInline, BlogPostTagInline]
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


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = [
        'post',
        'title',
        'order',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['title', 'description', 'post__title']
    readonly_fields = ['created_at']


@admin.register(BlogPostTag)
class BlogPostTagAdmin(admin.ModelAdmin):
    list_display = [
        'post',
        'tag',
        'created_at'
    ]
    list_filter = ['tag', 'created_at']
    search_fields = ['post__title', 'tag__name']
    readonly_fields = ['created_at']

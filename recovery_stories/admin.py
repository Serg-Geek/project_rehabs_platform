from django.contrib import admin
from .models import RecoveryCategory, RecoveryStory, RecoveryTag, RecoveryStoryTag, RecoveryStoryImage

class RecoveryStoryImageInline(admin.TabularInline):
    model = RecoveryStoryImage
    extra = 1

class RecoveryStoryTagInline(admin.TabularInline):
    model = RecoveryStoryTag
    extra = 1

@admin.register(RecoveryStory)
class RecoveryStoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'author',
        'is_published',
        'publish_date',
        'views'
    ]
    list_filter = [
        'is_published',
        'category',
        'publish_date',
        'rehab_center'
    ]
    search_fields = [
        'title',
        'content',
        'excerpt',
        'meta_description'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views']
    inlines = [RecoveryStoryImageInline, RecoveryStoryTagInline]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'slug',
                'category',
                'author',
                'rehab_center',
                'excerpt',
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
            )
        }),
        ('Публикация', {
            'fields': (
                'is_published',
                'publish_date',
            )
        }),
    )

@admin.register(RecoveryCategory)
class RecoveryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(RecoveryTag)
class RecoveryTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'is_system']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active', 'is_system']

@admin.register(RecoveryStoryTag)
class RecoveryStoryTagAdmin(admin.ModelAdmin):
    list_display = ['story', 'tag']
    list_filter = ['tag']
    search_fields = ['story__title', 'tag__name']

@admin.register(RecoveryStoryImage)
class RecoveryStoryImageAdmin(admin.ModelAdmin):
    list_display = ['story', 'title', 'order']
    list_filter = ['story']
    search_fields = ['story__title', 'title']

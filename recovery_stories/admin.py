from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from .models import RecoveryStory, RecoveryCategory, RecoveryTag, RecoveryStoryTag, RecoveryStoryImage

class RecoveryStoryImageInline(admin.TabularInline):
    model = RecoveryStoryImage
    extra = 1

class RecoveryStoryTagInline(admin.TabularInline):
    model = RecoveryStoryTag
    extra = 1

@admin.register(RecoveryStory)
class RecoveryStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'facility', 'is_published', 'publish_date')
    list_filter = ('category', 'is_published', 'content_type')
    search_fields = ('title', 'content', 'author')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [RecoveryStoryImageInline, RecoveryStoryTagInline]
    date_hierarchy = 'publish_date'

@admin.register(RecoveryCategory)
class RecoveryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order')
    list_filter = ('parent',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(RecoveryTag)
class RecoveryTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_system')
    list_filter = ('is_active', 'is_system')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

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

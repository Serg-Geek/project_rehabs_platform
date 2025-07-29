from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from facilities.utils import CustomJSONEncoder
from .models import (
    ServiceCategory,
    TherapyMethod,
    Service,
    FacilityService,
    ServicePrice
)

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'parent', 'order', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
    )

    def get_json_encoder(self):
        return CustomJSONEncoder

@admin.register(TherapyMethod)
class TherapyMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
    )

    def get_json_encoder(self):
        return CustomJSONEncoder

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_categories', 'is_active', 'display_priority', 'is_rehabilitation_program']
    list_filter = ['categories', 'is_active', 'display_priority', 'is_rehabilitation_program']
    search_fields = ['name', 'description']
    filter_horizontal = ['categories']
    exclude = ['slug']
    ordering = ['-display_priority', 'name']
    fieldsets = (
        (None, {
            'fields': ('name', 'categories', 'description', 'is_active', 'is_rehabilitation_program', 'display_priority')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
    )

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = _('Категории')

    def get_json_encoder(self):
        return CustomJSONEncoder

@admin.register(FacilityService)
class FacilityServiceAdmin(admin.ModelAdmin):
    list_display = ['get_facility_name', 'service', 'price', 'is_active']
    list_filter = ['content_type', 'service', 'is_active']
    search_fields = ['service__name']
    filter_horizontal = ['specialists']

    def get_facility_name(self, obj):
        return str(obj.facility)
    get_facility_name.short_description = _('Учреждение')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            # Ограничиваем выбор только моделями учреждений
            kwargs["queryset"] = ContentType.objects.filter(
                model__in=['clinic', 'rehabcenter', 'privatedoctor']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

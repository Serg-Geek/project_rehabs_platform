from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
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

@admin.register(TherapyMethod)
class TherapyMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'duration', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    exclude = ['slug']

@admin.register(FacilityService)
class FacilityServiceAdmin(admin.ModelAdmin):
    list_display = ['get_facility_name', 'service', 'price', 'is_active']
    list_filter = ['content_type', 'service', 'is_active']
    search_fields = ['service__name']
    filter_horizontal = ['specialists']
    raw_id_fields = ['content_type']

    def get_facility_name(self, obj):
        return str(obj.facility)
    get_facility_name.short_description = _('Учреждение')

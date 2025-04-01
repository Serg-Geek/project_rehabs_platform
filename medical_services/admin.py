from django.contrib import admin
from .models import (
    ServiceCategory,
    TherapyMethod,
    Service,
    FacilityService,
    ServicePrice
)

class ServicePriceInline(admin.TabularInline):
    model = ServicePrice
    extra = 1

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

@admin.register(TherapyMethod)
class TherapyMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'duration',
        'is_active'
    ]
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FacilityService)
class FacilityServiceAdmin(admin.ModelAdmin):
    list_display = [
        'facility',
        'service',
        'price',
        'is_active'
    ]
    list_filter = ['facility', 'service', 'is_active']
    search_fields = ['facility__name', 'service__name']
    filter_horizontal = ['specialists']
    inlines = [ServicePriceInline]

@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = [
        'facility_service',
        'price',
        'start_date',
        'end_date'
    ]
    list_filter = ['start_date', 'end_date']
    search_fields = [
        'facility_service__facility__name',
        'facility_service__service__name'
    ]

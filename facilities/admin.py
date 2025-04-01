from django.contrib import admin
from .models import (
    OrganizationType,
    MedicalFacility,
    Clinic,
    RehabCenter,
    FacilityImage,
    FacilityDocument
)

class FacilityImageInline(admin.TabularInline):
    model = FacilityImage
    extra = 1

class FacilityDocumentInline(admin.TabularInline):
    model = FacilityDocument
    extra = 1

@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

class BaseFacilityAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'organization_type',
        'city',
        'phone',
        'email',
        'is_active'
    ]
    list_filter = ['organization_type', 'city__region', 'city', 'is_active']
    search_fields = ['name', 'description', 'address']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [FacilityImageInline, FacilityDocumentInline]

@admin.register(MedicalFacility)
class MedicalFacilityAdmin(BaseFacilityAdmin):
    pass

@admin.register(Clinic)
class ClinicAdmin(BaseFacilityAdmin):
    list_display = BaseFacilityAdmin.list_display + ['emergency_support', 'has_hospital']
    list_filter = BaseFacilityAdmin.list_filter + ['emergency_support', 'has_hospital']

@admin.register(RehabCenter)
class RehabCenterAdmin(BaseFacilityAdmin):
    list_display = BaseFacilityAdmin.list_display + ['capacity', 'program_duration']
    list_filter = BaseFacilityAdmin.list_filter

@admin.register(FacilityImage)
class FacilityImageAdmin(admin.ModelAdmin):
    list_display = ['facility', 'image_type', 'title', 'is_main', 'order']
    list_filter = ['image_type', 'is_main']
    search_fields = ['facility__name', 'title', 'description']
    ordering = ['facility', 'order']

@admin.register(FacilityDocument)
class FacilityDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'facility',
        'document_type',
        'title',
        'number',
        'issue_date',
        'expiry_date',
        'is_active'
    ]
    list_filter = ['document_type', 'is_active', 'issue_date', 'expiry_date']
    search_fields = ['facility__name', 'title', 'number']
    ordering = ['-created_at']

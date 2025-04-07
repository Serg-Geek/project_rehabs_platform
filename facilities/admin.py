from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    OrganizationType,
    Clinic,
    RehabCenter,
    FacilityImage,
    FacilityDocument
)
from staff.models import FacilitySpecialist
from django.utils.translation import gettext_lazy as _

class FacilityImageInline(GenericTabularInline):
    model = FacilityImage
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 1
    fields = ['image', 'image_type', 'title', 'description', 'is_main', 'order']
    verbose_name = _('Фото')
    verbose_name_plural = _('Фотографии')

class FacilityDocumentInline(GenericTabularInline):
    model = FacilityDocument
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 1
    fields = ['document_type', 'title', 'document', 'number', 'issue_date', 'expiry_date', 'is_active']
    verbose_name = _('Документ')
    verbose_name_plural = _('Документы')

class FacilitySpecialistInline(GenericTabularInline):
    model = FacilitySpecialist
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 1
    fields = ['first_name', 'last_name', 'middle_name', 'position', 'schedule', 'specializations', 'experience_years', 'is_active']
    verbose_name = _('Специалист')
    verbose_name_plural = _('Специалисты')

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
    inlines = [FacilityImageInline, FacilityDocumentInline, FacilitySpecialistInline]

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
    list_display = ['facility', 'image_type', 'title']
    list_filter = ['image_type']
    search_fields = ['facility__name', 'title']
    ordering = ['facility']

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

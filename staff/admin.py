from django.contrib import admin
from .models import (
    MedicalSpecialist,
    FacilitySpecialist,
    PrivateSpecialist,
    Specialization,
    SpecialistDocument
)

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']

@admin.register(MedicalSpecialist)
class MedicalSpecialistAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name',
        'experience_years',
        'is_active'
    ]
    list_filter = [
        'is_active',
        'specializations',
        'experience_years'
    ]
    search_fields = [
        'last_name',
        'first_name',
        'middle_name',
        'biography'
    ]
    filter_horizontal = ['specializations']
    exclude = ['slug']

@admin.register(FacilitySpecialist)
class FacilitySpecialistAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name',
        'facility',
        'position',
        'is_active'
    ]
    list_filter = [
        'is_active',
        'facility',
        'position'
    ]
    search_fields = [
        'last_name',
        'first_name',
        'middle_name',
        'facility__name',
        'position'
    ]

@admin.register(PrivateSpecialist)
class PrivateSpecialistAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name',
        'consultation_price',
        'available_online',
        'is_active'
    ]
    list_filter = [
        'is_active',
        'available_online',
        'regions_of_work'
    ]
    search_fields = [
        'last_name',
        'first_name',
        'middle_name',
        'consultation_address',
        'license_number'
    ]
    filter_horizontal = ['regions_of_work']

@admin.register(SpecialistDocument)
class SpecialistDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'specialist',
        'document_type',
        'title',
        'issue_date',
        'is_active'
    ]
    list_filter = [
        'is_active',
        'document_type',
        'issue_date',
        'expiry_date'
    ]
    search_fields = [
        'specialist__last_name',
        'specialist__first_name',
        'title',
        'number'
    ]

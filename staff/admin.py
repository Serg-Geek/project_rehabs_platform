from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    FacilitySpecialist,
    Specialization,
    SpecialistDocument
)

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name', 'description']

@admin.register(FacilitySpecialist)
class FacilitySpecialistAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name',
        'position',
        'get_facility_name',
        'is_active'
    ]
    list_filter = [
        'is_active',
        'position',
        'content_type'
    ]
    search_fields = [
        'last_name',
        'first_name',
        'middle_name',
        'position'
    ]
    filter_horizontal = ['specializations']
    exclude = ['slug']
    
    def get_facility_name(self, obj):
        return str(obj.facility) if obj.facility else '-'
    get_facility_name.short_description = 'Учреждение'

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

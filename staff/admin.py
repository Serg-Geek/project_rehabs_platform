from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    FacilitySpecialist,
    Specialization,
    SpecialistDocument
)
from django.utils.text import slugify
from django.db.models import Q
from transliterate import slugify as transliterate_slugify

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

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
    exclude = ['content_type', 'object_id']
    
    def get_facility_name(self, obj):
        return str(obj.facility) if obj.facility else '-'
    get_facility_name.short_description = 'Учреждение'
    
    def save_model(self, request, obj, form, change):
        if not obj.slug:
            # Транслитерируем имя и фамилию
            transliterated_last_name = transliterate_slugify(obj.last_name)
            transliterated_first_name = transliterate_slugify(obj.first_name)
            
            # Формируем базовый слаг
            base_slug = f"{transliterated_last_name}-{transliterated_first_name}"
            slug = base_slug
            
            # Проверяем, существует ли уже такой слаг
            counter = 1
            while FacilitySpecialist.objects.filter(Q(slug=slug) & ~Q(pk=obj.pk)).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            obj.slug = slug
            
        super().save_model(request, obj, form, change)

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

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    OrganizationType,
    Clinic,
    RehabCenter,
    FacilityImage,
    FacilityDocument,
    Review
)
from staff.models import FacilitySpecialist
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from .utils import CustomJSONEncoder

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
        'id',
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
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'organization_type', 'city', 'address', 'phone', 'email', 'website', 'description', 'is_active')
        }),
    )

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
    list_display = ['get_facility_name', 'image_type', 'title', 'is_main', 'order']
    list_filter = ['image_type', 'content_type']
    search_fields = ['title', 'description']
    ordering = ['order', 'created_at']
    fields = [
        'content_type',
        'object_id',
        'image',
        'image_type',
        'title',
        'description',
        'is_main',
        'order'
    ]
    
    def get_facility_name(self, obj):
        return str(obj.facility)
    get_facility_name.short_description = _('Учреждение')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(
                model__in=['clinic', 'rehabcenter']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_json_encoder(self):
        return CustomJSONEncoder

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj and obj.facility:
            extra_context['title'] = f"{obj.get_image_type_display()} - {obj.facility.name}"
        return super().change_view(request, object_id, form_url, extra_context)

@admin.register(FacilityDocument)
class FacilityDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'document_type',
        'title',
        'number',
        'issue_date',
        'expiry_date',
        'is_active'
    ]
    list_filter = ['document_type', 'is_active', 'issue_date', 'expiry_date']
    search_fields = ['title', 'number']
    ordering = ['-created_at']
    exclude = ['content_type', 'object_id']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'facility',
        'rating',
        'content',
        'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = ['content', 'facility__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

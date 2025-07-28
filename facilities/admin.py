from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    OrganizationType,
    Clinic,
    RehabCenter,
    FacilityImage,
    FacilityDocument,
    PrivateDoctor
)
from staff.models import FacilitySpecialist
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from .utils import CustomJSONEncoder

class FacilityImageInline(GenericTabularInline):
    """
    Inline admin for facility images.
    """
    model = FacilityImage
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 1
    fields = ['image', 'image_type', 'title', 'description', 'is_main', 'order']
    verbose_name = _('Фото')
    verbose_name_plural = _('Фотографии')

class FacilityDocumentInline(GenericTabularInline):
    """
    Inline admin for facility documents.
    """
    model = FacilityDocument
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 1
    fields = ['document_type', 'title', 'document', 'number', 'issue_date', 'expiry_date', 'is_active']
    verbose_name = _('Документ')
    verbose_name_plural = _('Документы')

class FacilitySpecialistInline(GenericTabularInline):
    """
    Inline admin for facility specialists.
    """
    model = FacilitySpecialist
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    extra = 1
    fields = ['first_name', 'last_name', 'middle_name', 'position', 'schedule', 'specializations', 'experience_years', 'is_active']
    verbose_name = _('Специалист')
    verbose_name_plural = _('Специалисты')

@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    """
    Admin for organization types.
    """
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

class BaseFacilityAdmin(admin.ModelAdmin):
    """
    Base admin class for facility models.
    """
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
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'meta_image'),
            'classes': ('collapse',),
        }),
    )

    def get_json_encoder(self):
        """
        Get custom JSON encoder for admin.
        
        Returns:
            CustomJSONEncoder: Custom JSON encoder class
        """
        return CustomJSONEncoder

@admin.register(Clinic)
class ClinicAdmin(BaseFacilityAdmin):
    """
    Admin for clinic model.
    """
    list_display = BaseFacilityAdmin.list_display + ['emergency_support', 'has_hospital']
    list_filter = BaseFacilityAdmin.list_filter + ['emergency_support', 'has_hospital']

@admin.register(RehabCenter)
class RehabCenterAdmin(BaseFacilityAdmin):
    """
    Admin for rehabilitation center model.
    """
    list_display = BaseFacilityAdmin.list_display + ['rehabilitation_programs_list']
    list_filter = BaseFacilityAdmin.list_filter
    readonly_fields = ['rehabilitation_programs_list']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'organization_type', 'city', 'address', 'phone', 'email', 'website', 'description', 'is_active', 'rehabilitation_programs_list')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'meta_image'),
            'classes': ('collapse',),
        }),
    )

    def rehabilitation_programs_list(self, obj):
        """
        Get list of rehabilitation programs for display.
        
        Args:
            obj: RehabCenter instance
            
        Returns:
            str: Comma-separated list of program names
        """
        from medical_services.models import FacilityService
        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(obj)
        programs = FacilityService.objects.filter(
            content_type=ct,
            object_id=obj.id
        ).values_list('service__name', flat=True)
        return ', '.join(programs) if programs else 'Нет программ'
    rehabilitation_programs_list.short_description = _('Программы реабилитации')

@admin.register(FacilityImage)
class FacilityImageAdmin(admin.ModelAdmin):
    """
    Admin for facility images.
    """
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
        """
        Get facility name for display.
        
        Args:
            obj: FacilityImage instance
            
        Returns:
            str: Facility name
        """
        return str(obj.content_object) if obj.content_object else 'Unknown'
    get_facility_name.short_description = _('Учреждение')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Customize foreign key field for content type.
        
        Args:
            db_field: Database field
            request: HTTP request object
            **kwargs: Additional keyword arguments
            
        Returns:
            FormField: Customized form field
        """
        if db_field.name == 'content_type':
            kwargs['queryset'] = ContentType.objects.filter(
                model__in=['clinic', 'rehabcenter', 'privatedoctor']
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_json_encoder(self):
        """
        Get custom JSON encoder for admin.
        
        Returns:
            CustomJSONEncoder: Custom JSON encoder class
        """
        return CustomJSONEncoder

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Custom change view with additional context.
        
        Args:
            request: HTTP request object
            object_id: Object ID
            form_url: Form URL
            extra_context: Additional context
            
        Returns:
            HttpResponse: Rendered change view
        """
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = True
        return super().change_view(request, object_id, form_url, extra_context)

@admin.register(FacilityDocument)
class FacilityDocumentAdmin(admin.ModelAdmin):
    """
    Admin for facility documents.
    """
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

@admin.register(PrivateDoctor)
class PrivateDoctorAdmin(BaseFacilityAdmin):
    """
    Admin for private doctor model.
    """
    list_display = [
        'get_full_name',
        'organization_type',
        'city',
        'phone',
        'consultation_price',
        'is_active'
    ]
    list_filter = [
        'organization_type',
        'city__region',
        'city',
        'is_active',
        'home_visits',
        'emergency_available',
        'weekend_work',
        'online_consultations',
        'video_consultations',
        'insurance_accepted'
    ]
    search_fields = [
        'first_name',
        'last_name',
        'middle_name',
        'phone',
        'email',
        'address',
        'specializations__name'
    ]
    filter_horizontal = ['specializations']
    prepopulated_fields = {'slug': ('last_name', 'first_name')}
    inlines = [FacilityImageInline, FacilityDocumentInline]
    
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'middle_name', 'slug', 'organization_type', 'city', 'address', 'phone', 'email', 'website', 'description', 'is_active')
        }),
        (_('Специализация'), {
            'fields': ('specializations', 'experience_years', 'consultation_price', 'home_visits', 'emergency_available')
        }),
        (_('Расписание'), {
            'fields': ('weekend_work', 'online_consultations', 'video_consultations', 'insurance_accepted')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'meta_image'),
            'classes': ('collapse',),
        }),
    )
    
    def get_full_name(self, obj):
        """
        Get full name for display.
        
        Args:
            obj: PrivateDoctor instance
            
        Returns:
            str: Full name
        """
        return obj.get_full_name()
    get_full_name.short_description = _('ФИО')
    get_full_name.admin_order_field = 'last_name'

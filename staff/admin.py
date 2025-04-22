from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from .models import (
    FacilitySpecialist,
    Specialization,
    SpecialistDocument
)
from django.utils.text import slugify
from django.db.models import Q
from transliterate import slugify as transliterate_slugify
from django.forms import ModelForm
from django import forms
from facilities.models import Clinic, RehabCenter

class FacilitySpecialistForm(ModelForm):
    facility_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            model__in=['clinic', 'rehabcenter']
        ),
        label=_('Тип учреждения')
    )
    facility_id = forms.IntegerField(label=_('ID учреждения'))

    class Meta:
        model = FacilitySpecialist
        exclude = ['content_type', 'object_id', 'slug']
        widgets = {
            'photo': admin.widgets.AdminFileWidget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.content_type:
            self.initial['facility_type'] = self.instance.content_type
            self.initial['facility_id'] = self.instance.object_id

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.content_type = self.cleaned_data['facility_type']
        instance.object_id = self.cleaned_data['facility_id']
        if commit:
            instance.save()
        return instance

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FacilitySpecialist)
class FacilitySpecialistAdmin(admin.ModelAdmin):
    form = FacilitySpecialistForm
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
    
    def get_facility_name(self, obj):
        return str(obj.facility) if obj.facility else '-'
    get_facility_name.short_description = _('Учреждение')
    
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

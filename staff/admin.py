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
from django.core.files.uploadedfile import UploadedFile
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.template.response import TemplateResponse
from django.shortcuts import redirect

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
        exclude = ['content_type', 'object_id', 'slug', 'photo']

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
        'is_active',
        'photo_display'
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
    
    fieldsets = (
        (None, {
            'fields': ('last_name', 'first_name', 'middle_name'),
        }),
        (_('Учреждение'), {
            'fields': ('facility_type', 'facility_id', 'position', 'schedule'),
        }),
        (_('Информация о специалисте'), {
            'fields': ('specializations', 'experience_years', 'education', 'biography', 'achievements'),
        }),
        (_('Статус'), {
            'fields': ('is_active',),
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/upload-photo/',
                self.admin_site.admin_view(self.upload_photo_view),
                name='staff_facilityspecialist_upload_photo',
            ),
            path(
                '<path:object_id>/delete-photo/',
                self.admin_site.admin_view(self.delete_photo_view),
                name='staff_facilityspecialist_delete_photo',
            ),
        ]
        return custom_urls + urls
    
    def upload_photo_view(self, request, object_id):
        """Загрузка фото специалиста"""
        obj = self.get_object(request, object_id)
        
        # Если GET-запрос, отображаем шаблон для загрузки
        if request.method == 'GET':
            context = {
                'opts': self.model._meta,
                'object_id': object_id,
                'original': obj,
                'title': _('Загрузить фото'),
                'app_label': self.model._meta.app_label,
            }
            return TemplateResponse(
                request,
                'admin/staff/facilityspecialist/upload_photo.html',
                context
            )
            
        # Если POST-запрос, обрабатываем загрузку файла
        elif request.method == 'POST' and 'photo' in request.FILES:
            try:
                # Получаем файл
                photo_file = request.FILES['photo']
                
                # Сохраняем его
                obj.photo = photo_file
                obj.save()
                
                # Очищаем объект из request
                request.FILES.clear()
                
                # Добавляем сообщение об успехе
                messages.success(request, _('Фото успешно загружено'))
                
                # Возвращаем скрипт перенаправления без использования объекта в сессии
                html = f"""
                <html>
                <body>
                <script>
                    window.location.href = '/admin/staff/facilityspecialist/{object_id}/change/';
                </script>
                </body>
                </html>
                """
                return HttpResponse(html)
            except Exception as e:
                messages.error(request, f'Ошибка при загрузке фото: {str(e)}')
                # Возвращаем скрипт перенаправления с сообщением об ошибке
                html = f"""
                <html>
                <body>
                <script>
                    window.location.href = '/admin/staff/facilityspecialist/{object_id}/change/';
                </script>
                </body>
                </html>
                """
                return HttpResponse(html)
        
        # Если другой тип запроса или нет файла, просто перенаправляем
        html = f"""
        <html>
        <body>
        <script>
            window.location.href = '/admin/staff/facilityspecialist/{object_id}/change/';
        </script>
        </body>
        </html>
        """
        return HttpResponse(html)
    
    def delete_photo_view(self, request, object_id):
        """Удаление фото специалиста"""
        obj = self.get_object(request, object_id)
        
        if obj.photo:
            try:
                # Сохраняем имя файла для логирования
                filename = obj.photo.name
                
                # Удаляем файл
                obj.photo.delete(save=False)
                obj.photo = None
                obj.save()
                
                # Добавляем сообщение об успехе
                messages.success(request, _('Фото успешно удалено'))
            except Exception as e:
                messages.error(request, f'Ошибка при удалении фото: {str(e)}')
        
        # Возвращаем скрипт перенаправления без использования объекта в сессии
        html = f"""
        <html>
        <body>
        <script>
            window.location.href = '/admin/staff/facilityspecialist/{object_id}/change/';
        </script>
        </body>
        </html>
        """
        return HttpResponse(html)
    
    def photo_display(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.photo.url
            )
        return format_html('<span>-</span>')
    photo_display.short_description = _('Фото')
    
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
        
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if obj and obj.photo:
            try:
                # Используем только URL, а не объект
                photo_url = obj.photo.url
                context.update({
                    'photo_url': photo_url,
                    'has_photo': True,
                    'object_id': obj.pk,
                    'upload_photo_url': f'/admin/staff/facilityspecialist/{obj.pk}/upload-photo/',
                    'delete_photo_url': f'/admin/staff/facilityspecialist/{obj.pk}/delete-photo/',
                })
            except Exception:
                # Если возникла ошибка с файлом, не показываем его
                context.update({
                    'has_photo': False,
                    'object_id': obj.pk,
                    'upload_photo_url': f'/admin/staff/facilityspecialist/{obj.pk}/upload-photo/',
                })
        elif obj:
            context.update({
                'has_photo': False,
                'object_id': obj.pk,
                'upload_photo_url': f'/admin/staff/facilityspecialist/{obj.pk}/upload-photo/',
            })
        return super().render_change_form(request, context, add, change, form_url, obj)

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

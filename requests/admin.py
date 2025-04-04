from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import AnonymousRequest, RequestNote, RequestStatusHistory, RequestActionLog
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

class RequestNoteInline(admin.TabularInline):
    model = RequestNote
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    fields = ['text', 'is_important', 'created_at', 'created_by']

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name__in=['Manager', 'Operator']).exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name='Manager').exists()

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая заметка
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class RequestStatusHistoryInline(admin.TabularInline):
    model = RequestStatusHistory
    extra = 0
    ordering = ['-changed_at']
    readonly_fields = ['changed_at', 'changed_by']
    fields = ['old_status', 'new_status', 'comment', 'changed_at', 'changed_by']

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.changed_by = request.user
        super().save_model(request, obj, form, change)

class RequestActionLogInline(admin.TabularInline):
    model = RequestActionLog
    extra = 0
    readonly_fields = ['created_at', 'user']
    fields = ['action', 'details', 'created_at', 'user']

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(AnonymousRequest)
class AnonymousRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'get_source', 'status', 'priority', 'admin_note', 'created_at', 'assigned_to')
    list_filter = ('status', 'request_type', 'priority', 'created_at')
    search_fields = ('id', 'name', 'phone', 'email', 'patient_name', 'message')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_source(self, obj):
        if obj.request_type == 'consultation':
            return 'Форма на сайте'
        elif obj.request_type == 'phone':
            return 'Телефонный звонок'
        return obj.get_request_type_display()
    get_source.short_description = 'Источник'
    
    def admin_note(self, obj):
        # Получаем последнюю заметку к заявке
        note = obj.notes.order_by('-created_at').first()
        if note:
            return note.text[:50] + '...' if len(note.text) > 50 else note.text
        return '-'
    admin_note.short_description = 'Заметка к заявке'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('request_type', 'name', 'phone', 'email', 'message')
        }),
        ('Информация о пациенте', {
            'fields': ('patient_name', 'patient_age', 'preferred_contact_time')
        }),
        ('Предпочтения', {
            'fields': ('preferred_facility', 'preferred_service')
        }),
        ('Статус и приоритет', {
            'fields': ('status', 'priority')
        }),
        ('Комиссия', {
            'fields': ('commission_amount', 'commission_received_date', 'commission_document')
        }),
        ('Назначение', {
            'fields': ('assigned_to',)
        }),
        ('Системная информация', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая заявка
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('assigned_to', 'created_by', 'updated_by').prefetch_related('notes')

@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('request', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status', 'changed_at', 'changed_by')
    search_fields = ('request__name', 'request__phone')
    readonly_fields = ('changed_at', 'changed_by')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.changed_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(RequestNote)
class RequestNoteAdmin(admin.ModelAdmin):
    list_display = ('get_request_info', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('text', 'request__name', 'request__phone', 'request__id')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_request_info(self, obj):
        return f"Заявка #{obj.request.id} - {obj.request.name}"
    get_request_info.short_description = 'Заявка'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая заметка
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(RequestActionLog)
class RequestActionLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'user', 'action', 'created_at')
    list_filter = ('action', 'created_at', 'user')
    search_fields = ('details', 'request__name', 'request__phone')
    readonly_fields = ('created_at', 'user')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.user = request.user
        super().save_model(request, obj, form, change)

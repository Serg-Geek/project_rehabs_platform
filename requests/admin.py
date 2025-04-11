from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import AnonymousRequest, RequestNote, RequestStatusHistory, RequestActionLog, Request
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

class RequestNoteInline(admin.StackedInline):
    model = RequestNote
    extra = 0
    verbose_name_plural = _('Заметки')

class RequestStatusHistoryInline(admin.TabularInline):
    model = RequestStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'comment', 'changed_at', 'changed_by')
    verbose_name_plural = _('История статусов')

class RequestActionLogInline(admin.TabularInline):
    model = RequestActionLog
    extra = 0
    readonly_fields = ['created_at', 'user']
    fields = ['action', 'details', 'created_at', 'user']

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'addiction_type', 'contact_type', 'get_full_name', 'pseudonym', 'email', 'phone', 'responsible_staff', 'created_at')
    list_filter = ('status', 'addiction_type', 'contact_type', 'responsible_staff', 'created_at')
    search_fields = ('first_name', 'last_name', 'pseudonym', 'email', 'phone', 'emergency_contact', 'emergency_phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('status', 'addiction_type', 'responsible_staff')
        }),
        (_('Персональная информация'), {
            'fields': ('contact_type', 'first_name', 'last_name', 'pseudonym', 'email', 'phone')
        }),
        (_('Контактная информация'), {
            'fields': ('emergency_contact', 'emergency_phone')
        }),
        (_('Медицинская информация'), {
            'fields': ('medical_history', 'treatment_plan')
        }),
        (_('Дополнительно'), {
            'fields': ('notes', 'created_at', 'updated_at')
        })
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('ФИО')

@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('request', 'old_status', 'new_status', 'changed_at', 'changed_by')
    list_filter = ('old_status', 'new_status', 'changed_at')
    readonly_fields = ('request', 'old_status', 'new_status', 'comment', 'changed_at', 'changed_by')

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
    list_display = ('request', 'text', 'is_important', 'created_by', 'created_at')
    list_filter = ('is_important', 'created_at')
    search_fields = ('text', 'request__name', 'request__phone')

@admin.register(RequestActionLog)
class RequestActionLogAdmin(admin.ModelAdmin):
    list_display = ('request', 'action', 'user', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('details', 'request__name', 'request__phone')
    readonly_fields = ('request', 'user', 'action', 'details', 'created_at')

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

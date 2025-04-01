from django.contrib import admin
from .models import AnonymousRequest, RequestNote, RequestStatusHistory

class RequestNoteInline(admin.TabularInline):
    model = RequestNote
    extra = 1

class RequestStatusHistoryInline(admin.TabularInline):
    model = RequestStatusHistory
    extra = 0
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(AnonymousRequest)
class AnonymousRequestAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'request_type',
        'phone',
        'email',
        'status',
        'created_at'
    ]
    list_filter = [
        'request_type',
        'status',
        'created_at',
        'preferred_facility',
        'preferred_service'
    ]
    search_fields = [
        'name',
        'phone',
        'email',
        'message',
        'patient_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RequestNoteInline, RequestStatusHistoryInline]
    fieldsets = (
        ('Информация о заявителе', {
            'fields': (
                'request_type',
                'name',
                'phone',
                'email',
            )
        }),
        ('Информация о пациенте', {
            'fields': (
                'patient_name',
                'patient_age',
            )
        }),
        ('Детали обращения', {
            'fields': (
                'message',
                'preferred_contact_time',
                'preferred_facility',
                'preferred_service',
            )
        }),
        ('Статус', {
            'fields': (
                'status',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(RequestNote)
class RequestNoteAdmin(admin.ModelAdmin):
    list_display = [
        'request',
        'text',
        'is_important',
        'created_at'
    ]
    list_filter = ['is_important', 'created_at']
    search_fields = ['text', 'request__name']
    readonly_fields = ['created_at']

@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'request',
        'old_status',
        'new_status',
        'created_at'
    ]
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['request__name', 'comment']
    readonly_fields = ['created_at']

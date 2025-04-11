from django.contrib import admin
from .models import AccessLevel, AppPermission, UserAccess, AdminActionLog

@admin.register(AccessLevel)
class AccessLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'level_type', 'is_active']
    list_filter = ['level_type', 'is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_by', 'created_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'level_type', 'description', 'is_active')
        }),
        ('Дополнительная информация', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AppPermission)
class AppPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'app_label',
        'access_level',
        'can_view',
        'can_add',
        'can_change',
        'can_delete',
        'can_assign_responsible',
        'can_change_status'
    ]
    list_filter = ['app_label', 'access_level']
    search_fields = ['app_label']
    fieldsets = (
        (None, {
            'fields': ('app_label', 'access_level')
        }),
        ('Разрешения', {
            'fields': (
                'can_view',
                'can_add',
                'can_change',
                'can_delete',
                'can_assign_responsible',
                'can_change_status'
            )
        }),
    )

@admin.register(UserAccess)
class UserAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'access_level', 'is_active', 'valid_from', 'valid_until']
    list_filter = ['is_active', 'access_level']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'access_level', 'is_active')
        }),
        ('Срок действия', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Дополнительная информация', {
            'fields': ('granted_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'app_label', 'model_name', 'created_at']
    list_filter = ['action', 'app_label', 'model_name', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'app_label', 'model_name', 'object_id')
        }),
        ('Изменения', {
            'fields': ('changes',)
        }),
        ('Дополнительная информация', {
            'fields': ('access_level', 'ip_address', 'created_at'),
            'classes': ('collapse',)
        }),
    )

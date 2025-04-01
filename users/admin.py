from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, PatientProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'

class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Профиль пациента'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined'
    ]
    list_filter = [
        'is_staff',
        'is_active',
        'groups',
        'date_joined'
    ]
    search_fields = [
        'email',
        'username',
        'first_name',
        'last_name'
    ]
    ordering = ['-date_joined']
    inlines = [UserProfileInline, PatientProfileInline]
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Персональная информация', {
            'fields': (
                'username',
                'first_name',
                'last_name',
                'phone',
                'avatar',
            )
        }),
        ('Разрешения', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            )
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'birth_date',
        'gender',
        'created_at'
    ]
    list_filter = ['gender', 'created_at']
    search_fields = [
        'user__email',
        'user__username',
        'address'
    ]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'medical_record_number',
        'blood_type',
        'emergency_contact_name',
        'created_at'
    ]
    list_filter = ['blood_type', 'created_at']
    search_fields = [
        'user__email',
        'user__username',
        'medical_record_number',
        'emergency_contact_name'
    ]
    readonly_fields = ['created_at', 'updated_at']

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import User, UserProfile, UserActionLog

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'password')

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            raise forms.ValidationError(_('Роль обязательна для заполнения'))
        
        # Проверяем, что роль существует в списке допустимых ролей
        if role not in dict(User.Role.choices):
            raise forms.ValidationError(_('Недопустимая роль'))
            
        return role

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Пользователь с таким email уже существует'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Пользователь с таким именем уже существует'))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Профиль')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Админка пользователей с разными представлениями
    """
    add_form = UserCreationForm
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active', 'last_login')
    list_filter = ('role', 'is_active', 'last_login')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Персональная информация'), {'fields': ('username', 'first_name', 'last_name', 'phone', 'avatar')}),
        (_('Роли и права'), {'fields': ('role', 'is_active', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password', 'role'),
        }),
    )
    
    inlines = (UserProfileInline,)

    def has_add_permission(self, request):
        """
        Проверяем права на создание пользователей
        """
        if not request.user.is_staff:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        """
        Проверяем права на изменение пользователей
        """
        if not request.user.is_staff:
            return False
        if obj and obj.role == obj.Role.SUPERUSER and not request.user.is_superuser:
            return False
        return True

    def save_model(self, request, obj, form, change):
        """
        Переопределяем сохранение модели для установки правильных флагов
        в зависимости от роли
        """
        if obj.role == obj.Role.SUPERUSER:
            if not request.user.is_superuser:
                raise PermissionError(_('Только суперпользователь может создавать других суперпользователей'))
            obj.is_staff = True
            obj.is_superuser = True
        elif obj.role in [obj.Role.CONTENT_ADMIN, obj.Role.REQUESTS_ADMIN]:
            obj.is_staff = True
            obj.is_superuser = False
            
        # Сохраняем текущего пользователя для логирования
        obj._current_user = request.user
            
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.path.endswith('/staff-users/'):
            return qs.filter(role__in=[User.Role.SUPERUSER, User.Role.CONTENT_ADMIN, User.Role.REQUESTS_ADMIN])
        return qs

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('staff-users/', self.admin_site.admin_view(self.changelist_view), name='users_user_staff'),
        ]
        return custom_urls + urls

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date')
    search_fields = ('user__email', 'user__username')

@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__username', 'user__email', 'details')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'details', 'created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'model_name', 'object_id')
        }),
        (_('Детали'), {
            'fields': ('details',)
        }),
        (_('Даты'), {
            'fields': ('created_at', 'updated_at')
        })
    )

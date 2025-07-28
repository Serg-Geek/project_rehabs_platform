from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import (
    AnonymousRequest, RequestNote, RequestStatusHistory, 
    RequestActionLog, DependentRequest, RequestTemplate,
    DependentRequestNote, DependentRequestStatusHistory
)
from .forms import AnonymousRequestAdminForm, DependentRequestAdminForm
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

class RequestNoteInline(admin.StackedInline):
    """
    Inline admin for request notes.
    """
    model = RequestNote
    extra = 1
    verbose_name_plural = _('Заметки')
    readonly_fields = ('created_at', 'created_by')
    can_delete = False
    
    def save_model(self, request, obj, form, change):
        """
        Save model with automatic user assignment.
        
        Args:
            request: HTTP request object
            obj: Model instance to save
            form: Form instance
            change: Whether this is a change operation
        """
        if not change:  # Если это новая запись
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class RequestStatusHistoryInline(admin.TabularInline):
    """
    Inline admin for request status history (read-only).
    """
    model = RequestStatusHistory
    extra = 0
    fields = ('old_status', 'new_status', 'comment', 'changed_at', 'changed_by')
    readonly_fields = ('old_status', 'new_status', 'comment', 'changed_at', 'changed_by')
    verbose_name_plural = _('История статусов')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """
        Disable add permission for status history.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Disable change permission for status history.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

class RequestActionLogInline(admin.TabularInline):
    """
    Inline admin for request action logs (read-only).
    """
    model = RequestActionLog
    extra = 0
    readonly_fields = ['action', 'details', 'created_at', 'user']
    fields = ['action', 'details', 'created_at', 'user']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """
        Disable add permission for action logs.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Disable change permission for action logs.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

@admin.register(RequestStatusHistory)
class RequestStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin for request status history (read-only).
    """
    list_display = ('request', 'old_status', 'new_status', 'changed_at', 'changed_by')
    list_filter = ('old_status', 'new_status', 'changed_at')
    readonly_fields = ('request', 'old_status', 'new_status', 'comment', 'changed_at', 'changed_by')
    
    def has_add_permission(self, request):
        """
        Disable add permission.
        
        Args:
            request: HTTP request object
            
        Returns:
            bool: Always False
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Disable change permission.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable delete permission.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

@admin.register(RequestNote)
class RequestNoteAdmin(admin.ModelAdmin):
    """
    Admin for request notes.
    """
    list_display = ('request', 'text', 'is_important', 'created_by', 'created_at')
    list_filter = ('is_important', 'created_at')
    search_fields = ('text', 'request__name', 'request__phone')

@admin.register(RequestActionLog)
class RequestActionLogAdmin(admin.ModelAdmin):
    """
    Admin for request action logs (read-only).
    """
    list_display = ('request', 'action', 'user', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('details', 'request__name', 'request__phone')
    readonly_fields = ('request', 'user', 'action', 'details', 'created_at')

    def has_add_permission(self, request):
        """
        Disable add permission.
        
        Args:
            request: HTTP request object
            
        Returns:
            bool: Always False
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Disable change permission.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable delete permission.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

@admin.register(AnonymousRequest)
class AnonymousRequestAdmin(admin.ModelAdmin):
    """
    Admin for anonymous requests with custom form and actions.
    """
    form = AnonymousRequestAdminForm
    list_display = ('id', 'request_type', 'source', 'status', 'priority', 'name', 'phone', 'organization', 'organization_type', 'assigned_organization', 'created_at', 'assigned_to', 'print_report_button')
    list_filter = ('request_type', 'source', 'status', 'priority', 'organization_type', 'created_at')
    search_fields = ('name', 'phone', 'email', 'organization', 'message', 'assigned_organization')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'print_report_button')
    list_editable = ('status', 'priority', 'assigned_to')
    inlines = [RequestNoteInline, RequestStatusHistoryInline, RequestActionLogInline]
    
    fieldsets = (
        (None, {
            'fields': ('request_type', 'status', 'source', 'priority', 'print_report_button')
        }),
        (_('Контактная информация'), {
            'fields': ('name', 'phone', 'email', 'organization', 'preferred_contact_time'),
            'description': _('Для анонимных заявок укажите "Анонимный пользователь" в поле "Имя". Телефон обязателен для связи.')
        }),
        (_('Сообщение'), {
            'fields': ('message',)
        }),
        (_('Дополнительная информация'), {
            'fields': ('patient_name', 'patient_age', 'preferred_service')
        }),
        (_('Назначение учреждения'), {
            'fields': ('organization_type', 'organization_choice', 'assigned_organization'),
            'description': _('Выберите тип организации и конкретную организацию.'),
        }),
        (_('Управление комиссией'), {
            'fields': ('commission_amount', 'commission_received_date', 'commission_document'),
            'classes': ('collapse',),
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by', 'assigned_to'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_in_progress', 'mark_as_completed', 'assign_to_me', 'mark_as_high_priority']
    
    def mark_as_in_progress(self, request, queryset):
        """
        Mark selected requests as in progress.
        
        Args:
            request: HTTP request object
            queryset: Selected requests queryset
        """
        updated = queryset.update(status=AnonymousRequest.Status.IN_PROGRESS)
        self.message_user(
            request,
            f'Успешно обновлено {updated} заявок в статус "В работе"'
        )
    
    def mark_as_completed(self, request, queryset):
        """
        Mark selected requests as completed.
        
        Args:
            request: HTTP request object
            queryset: Selected requests queryset
        """
        updated = queryset.update(status=AnonymousRequest.Status.COMPLETED)
        self.message_user(
            request,
            f'Успешно обновлено {updated} заявок в статус "Завершено"'
        )
    
    def assign_to_me(self, request, queryset):
        """
        Assign selected requests to current user.
        
        Args:
            request: HTTP request object
            queryset: Selected requests queryset
        """
        updated = queryset.update(assigned_to=request.user)
        self.message_user(
            request,
            f'Успешно назначено {updated} заявок вам'
        )
    
    def mark_as_high_priority(self, request, queryset):
        """
        Mark selected requests as high priority.
        
        Args:
            request: HTTP request object
            queryset: Selected requests queryset
        """
        updated = queryset.update(priority=AnonymousRequest.Priority.HIGH)
        self.message_user(
            request,
            f'Успешно обновлено {updated} заявок в высокий приоритет'
        )
    
    def print_report_button(self, obj):
        """
        Generate print report button HTML.
        
        Args:
            obj: Request instance
            
        Returns:
            str: HTML for print button
        """
        if obj.pk:
            url = reverse('requests:print_report', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" target="_blank">Печать отчета</a>',
                url
            )
        return ""

    def save_model(self, request, obj, form, change):
        """
        Save model with automatic user assignment and status history tracking.
        
        Args:
            request: HTTP request object
            obj: Model instance to save
            form: Form instance
            change: Whether this is a change operation
        """
        if not change:  # Если это новая запись
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
            # Проверяем, изменился ли статус
            if 'status' in form.changed_data:
                old_status = form.initial.get('status')
                new_status = obj.status
                if old_status != new_status:
                    # Создаем запись в истории статусов
                    from .models import RequestStatusHistory
                    
                    # Получаем человекочитаемые названия статусов
                    old_status_display = dict(AnonymousRequest.Status.choices).get(old_status, old_status)
                    new_status_display = dict(AnonymousRequest.Status.choices).get(new_status, new_status)
                    
                    RequestStatusHistory.objects.create(
                        request=obj,
                        old_status=old_status,
                        new_status=new_status,
                        comment=f"Статус изменен с '{old_status_display}' на '{new_status_display}'",
                        changed_by=request.user
                    )
                    
                    # Создаем запись в логе действий
                    from .models import RequestActionLog
                    RequestActionLog.objects.create(
                        request=obj,
                        user=request.user,
                        action=RequestActionLog.Action.STATUS_CHANGE,
                        details=f"Статус изменен с '{old_status_display}' на '{new_status_display}' через админку"
                    )
        
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        """
        Get form with dynamic organization choices.
        
        Args:
            request: HTTP request object
            obj: Model instance
            **kwargs: Additional keyword arguments
            
        Returns:
            Form: Form class with updated choices
        """
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.organization_type:
            # Создаем временный экземпляр формы для вызова метода
            temp_form = form(instance=obj)
            form.base_fields['organization_choice'].widget.choices = \
                temp_form._get_organization_choices(obj.organization_type)
        return form

@admin.register(RequestTemplate)
class RequestTemplateAdmin(admin.ModelAdmin):
    """
    Admin for request templates.
    """
    list_display = ('name', 'request_type', 'is_active', 'created_at', 'created_by')
    list_filter = ('request_type', 'is_active', 'created_at')
    search_fields = ('name', 'template_text')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'request_type', 'is_active')
        }),
        (_('Шаблон'), {
            'fields': ('template_text',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Save model with automatic user assignment.
        
        Args:
            request: HTTP request object
            obj: Model instance to save
            form: Form instance
            change: Whether this is a change operation
        """
        if not change:  # Если это новая запись
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class DependentRequestNoteInline(admin.StackedInline):
    """
    Inline admin for dependent request notes.
    """
    model = DependentRequestNote
    extra = 1
    verbose_name_plural = _('Заметки')
    readonly_fields = ('created_at', 'created_by')
    can_delete = False

class DependentRequestStatusHistoryInline(admin.TabularInline):
    """
    Inline admin for dependent request status history (read-only).
    """
    model = DependentRequestStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'comment', 'changed_at', 'changed_by')
    verbose_name_plural = _('История статусов')
    can_delete = False

@admin.register(DependentRequest)
class DependentRequestAdmin(admin.ModelAdmin):
    """
    Admin for dependent requests with custom form and actions.
    """
    form = DependentRequestAdminForm
    list_display = ('id', 'addiction_type', 'contact_type', 'get_display_name', 'phone', 'status', 'organization_type', 'assigned_organization', 'created_at', 'print_report_button')
    list_filter = ('addiction_type', 'contact_type', 'status', 'organization_type', 'created_at')
    search_fields = ('first_name', 'last_name', 'pseudonym', 'phone', 'email', 'assigned_organization')
    readonly_fields = ('created_at', 'updated_at', 'print_report_button')
    inlines = [DependentRequestNoteInline, DependentRequestStatusHistoryInline]
    
    fieldsets = (
        (None, {
            'fields': ('addiction_type', 'contact_type', 'status', 'print_report_button')
        }),
        (_('Контактная информация'), {
            'fields': ('first_name', 'last_name', 'pseudonym', 'phone', 'email', 'age'),
            'description': _('Для анонимных заявок используйте псевдоним.')
        }),
        (_('Информация о зависимости'), {
            'fields': ('addiction_duration', 'current_condition', 'preferred_treatment')
        }),
        (_('Назначение учреждения'), {
            'fields': ('organization_type', 'organization_choice', 'assigned_organization'),
            'description': _('Выберите тип организации и конкретную организацию.'),
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_display_name(self, obj):
        """
        Get display name for dependent request.
        
        Args:
            obj: DependentRequest instance
            
        Returns:
            str: Display name
        """
        if obj.contact_type == DependentRequest.ContactType.ANONYMOUS:
            return obj.pseudonym or 'Анонимный'
        return f"{obj.last_name} {obj.first_name}".strip()
    
    def print_report_button(self, obj):
        """
        Generate print report button HTML.
        
        Args:
            obj: Request instance
            
        Returns:
            str: HTML for print button
        """
        if obj.pk:
            url = reverse('requests:print_report', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}" target="_blank">Печать отчета</a>',
                url
            )
        return ""

    def get_form(self, request, obj=None, **kwargs):
        """
        Get form with dynamic organization choices.
        
        Args:
            request: HTTP request object
            obj: Model instance
            **kwargs: Additional keyword arguments
            
        Returns:
            Form: Form class with updated choices
        """
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.organization_type:
            # Создаем временный экземпляр формы для вызова метода
            temp_form = form(instance=obj)
            form.base_fields['organization_choice'].widget.choices = \
                temp_form._get_organization_choices(obj.organization_type)
        return form

    def save_model(self, request, obj, form, change):
        """
        Save model with automatic user assignment and status history tracking.
        
        Args:
            request: HTTP request object
            obj: Model instance to save
            form: Form instance
            change: Whether this is a change operation
        """
        if not change:  # Если это новая запись
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
            # Проверяем, изменился ли статус
            if 'status' in form.changed_data:
                old_status = form.initial.get('status')
                new_status = obj.status
                if old_status != new_status:
                    # Создаем запись в истории статусов
                    from .models import DependentRequestStatusHistory
                    
                    # Получаем человекочитаемые названия статусов
                    old_status_display = dict(DependentRequest.Status.choices).get(old_status, old_status)
                    new_status_display = dict(DependentRequest.Status.choices).get(new_status, new_status)
                    
                    DependentRequestStatusHistory.objects.create(
                        request=obj,
                        old_status=old_status,
                        new_status=new_status,
                        comment=f"Статус изменен с '{old_status_display}' на '{new_status_display}'",
                        changed_by=request.user
                    )
        
        super().save_model(request, obj, form, change)

@admin.register(DependentRequestNote)
class DependentRequestNoteAdmin(admin.ModelAdmin):
    """
    Admin for dependent request notes.
    """
    list_display = ('request', 'text', 'is_important', 'created_by', 'created_at')
    list_filter = ('is_important', 'created_at')
    search_fields = ('text', 'request__first_name', 'request__last_name', 'request__phone')

@admin.register(DependentRequestStatusHistory)
class DependentRequestStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin for dependent request status history (read-only).
    """
    list_display = ('request', 'old_status', 'new_status', 'changed_at', 'changed_by')
    list_filter = ('old_status', 'new_status', 'changed_at')
    readonly_fields = ('request', 'old_status', 'new_status', 'comment', 'changed_at', 'changed_by')
    
    def has_add_permission(self, request):
        """
        Disable add permission.
        
        Args:
            request: HTTP request object
            
        Returns:
            bool: Always False
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Disable change permission.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable delete permission.
        
        Args:
            request: HTTP request object
            obj: Model instance
            
        Returns:
            bool: Always False
        """
        return False

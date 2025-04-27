from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import (
    AnonymousRequest, RequestNote, RequestStatusHistory, 
    RequestActionLog, Request, DependentRequest, RequestTemplate
)
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse

class RequestNoteInline(admin.StackedInline):
    model = RequestNote
    extra = 1
    verbose_name_plural = _('Заметки')
    readonly_fields = ('created_at', 'created_by')
    can_delete = False
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class RequestStatusHistoryInline(admin.TabularInline):
    model = RequestStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'comment', 'changed_at', 'changed_by')
    verbose_name_plural = _('История статусов')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

class RequestActionLogInline(admin.TabularInline):
    model = RequestActionLog
    extra = 0
    readonly_fields = ['action', 'details', 'created_at', 'user']
    fields = ['action', 'details', 'created_at', 'user']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

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

@admin.register(AnonymousRequest)
class AnonymousRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_type', 'source', 'status', 'priority', 'name', 'phone', 'organization', 'created_at', 'assigned_to', 'print_report_button')
    list_filter = ('request_type', 'source', 'status', 'priority', 'created_at')
    search_fields = ('name', 'phone', 'email', 'organization', 'message')
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
        updated = queryset.update(status=AnonymousRequest.Status.IN_PROGRESS, updated_by=request.user)
        # Создаем историю статусов
        for item in queryset:
            RequestStatusHistory.objects.create(
                request=item,
                old_status=item.status,
                new_status=AnonymousRequest.Status.IN_PROGRESS,
                changed_by=request.user,
                comment='Массовое изменение статуса через админ-панель'
            )
            # Создаем запись в логе действий
            RequestActionLog.objects.create(
                request=item,
                user=request.user,
                action=RequestActionLog.Action.STATUS_CHANGE,
                details=f'Изменен статус на {AnonymousRequest.Status.IN_PROGRESS}'
            )
        self.message_user(request, _(f'Обновлено {updated} заявок'))
    mark_as_in_progress.short_description = _('Отметить как "В обработке"')
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status=AnonymousRequest.Status.CLOSED, updated_by=request.user)
        # Создаем историю статусов и логи для каждой заявки
        for item in queryset:
            RequestStatusHistory.objects.create(
                request=item,
                old_status=item.status,
                new_status=AnonymousRequest.Status.CLOSED,
                changed_by=request.user,
                comment='Массовое изменение статуса через админ-панель'
            )
            RequestActionLog.objects.create(
                request=item,
                user=request.user,
                action=RequestActionLog.Action.STATUS_CHANGE,
                details=f'Изменен статус на {AnonymousRequest.Status.CLOSED}'
            )
        self.message_user(request, _(f'Закрыто {updated} заявок'))
    mark_as_completed.short_description = _('Отметить как "Закрыто"')
    
    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user, updated_by=request.user)
        for item in queryset:
            RequestActionLog.objects.create(
                request=item,
                user=request.user,
                action=RequestActionLog.Action.ASSIGN,
                details=f'Заявка назначена пользователю {request.user.get_full_name() or request.user.username}'
            )
        self.message_user(request, _(f'{updated} заявок назначено вам'))
    assign_to_me.short_description = _('Назначить мне')
    
    def mark_as_high_priority(self, request, queryset):
        updated = queryset.update(priority=AnonymousRequest.Priority.HIGH, updated_by=request.user)
        for item in queryset:
            RequestActionLog.objects.create(
                request=item,
                user=request.user,
                action=RequestActionLog.Action.UPDATE,
                details=f'Установлен высокий приоритет'
            )
        self.message_user(request, _(f'Установлен высокий приоритет для {updated} заявок'))
    mark_as_high_priority.short_description = _('Установить высокий приоритет')

    def print_report_button(self, obj):
        if obj.pk:
            url = reverse('requests:print_report', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button" style="background-color: #28a745;" target="_blank">'
                '<i class="fas fa-file-alt"></i> Печать отчета</a>',
                url
            )
        return ''
    print_report_button.short_description = _('Печать отчета')

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.created_by = request.user
        obj.updated_by = request.user
        
        # Отслеживаем изменение статуса
        if change and 'status' in form.changed_data:
            old_status = AnonymousRequest.objects.get(pk=obj.pk).status
            # Создаем запись в истории статусов
            RequestStatusHistory.objects.create(
                request=obj,
                old_status=old_status,
                new_status=obj.status,
                changed_by=request.user
            )
            # Создаем запись в логе действий
            RequestActionLog.objects.create(
                request=obj,
                user=request.user,
                action=RequestActionLog.Action.STATUS_CHANGE,
                details=f'Изменен статус с {old_status} на {obj.status}'
            )
        
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['phone'].required = True
        
        # Устанавливаем значение по умолчанию для поля name
        if obj is None:  # Только для новых объектов
            form.base_fields['name'].initial = "Анонимный пользователь"
        
        # Если заявка анонимная, поля имя и телефон обязательны для заполнения
        if obj is None or obj.source == AnonymousRequest.Source.PHONE_CALL:
            form.base_fields['name'].required = True
        
        return form

@admin.register(RequestTemplate)
class RequestTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'request_type', 'is_active', 'created_at', 'created_by')
    list_filter = ('request_type', 'is_active', 'created_at')
    search_fields = ('name', 'template_text')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'request_type', 'is_active')
        }),
        (_('Содержимое шаблона'), {
            'fields': ('template_text',)
        }),
        (_('Метаданные'), {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая запись
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(DependentRequest)
class DependentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'addiction_type', 'contact_type', 'get_display_name', 'phone', 'status', 'created_at', 'print_report_button')
    list_filter = ('addiction_type', 'contact_type', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'pseudonym', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at', 'print_report_button')
    
    fieldsets = (
        (None, {
            'fields': ('addiction_type', 'contact_type', 'status', 'print_report_button')
        }),
        (_('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'pseudonym', 'age', 'phone', 'email'),
            'description': _('Телефон является обязательным полем для связи. При анонимном контакте имя и фамилию указывать не нужно.')
        }),
        (_('Информация о зависимости'), {
            'fields': ('addiction_duration', 'previous_treatment', 'current_condition', 'preferred_treatment')
        }),
        (_('Контактная информация'), {
            'fields': ('emergency_contact', 'emergency_phone')
        }),
        (_('Дополнительно'), {
            'fields': ('notes', 'responsible_staff', 'created_at', 'updated_at')
        }),
    )
    
    def get_display_name(self, obj):
        if obj.contact_type == DependentRequest.ContactType.ANONYMOUS:
            return _('Анонимно')
        elif obj.contact_type == DependentRequest.ContactType.PSEUDONYM and obj.pseudonym:
            return obj.pseudonym
        return obj.get_full_name()
    get_display_name.short_description = _('Имя')
    
    def print_report_button(self, obj):
        if obj.pk:
            url = reverse('requests:print_report', args=[obj.pk]) + '?type=dependent'
            return format_html(
                '<a href="{}" class="button" style="background-color: #28a745;" target="_blank">'
                '<i class="fas fa-file-alt"></i> Печать отчета</a>',
                url
            )
        return ''
    print_report_button.short_description = _('Печать отчета')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['phone'].required = True
        
        # Устанавливаем динамические требования к полям в зависимости от типа контакта
        if not obj or obj.contact_type == DependentRequest.ContactType.REAL_NAME:
            form.base_fields['first_name'].required = True
            form.base_fields['last_name'].required = True
        elif not obj or obj.contact_type == DependentRequest.ContactType.PSEUDONYM:
            form.base_fields['pseudonym'].required = True
        
        return form
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

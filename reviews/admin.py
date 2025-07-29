from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import forms
from facilities.models import Clinic, RehabCenter
from .models import Review

class ReviewAdminForm(forms.ModelForm):
    """Форма для администрирования отзывов"""
    RATING_CHOICES = [
        (1, '★'),
        (2, '★★'),
        (3, '★★★'),
        (4, '★★★★'),
        (5, '★★★★★'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        label='Оценка',
        widget=forms.Select()
    )
    
    class Meta:
        model = Review
        fields = '__all__'
        exclude = ['created_by']  # Исключаем поле created_by, т.к. оно будет заполняться автоматически

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ('id', 'get_facility_name', 'author_display', 'get_rating_stars', 'short_content', 'created_at', 'is_published')
    list_filter = ('rating', 'is_published', 'created_at', 'content_type')
    search_fields = ('content', 'author_name')
    list_editable = ('is_published',)
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    fieldsets = (
        (None, {
            'fields': ('content_type', 'object_id')
        }),
        ('Информация об авторе', {
            'fields': ('author_name', 'author_age')
        }),
        ('Детали отзыва', {
            'fields': ('rating', 'content', 'is_published')
        }),
        ('Дополнительная информация', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def get_facility_name(self, obj):
        """Получить название учреждения"""
        if obj.facility:
            return str(obj.facility)
        return "—"
    get_facility_name.short_description = "Учреждение"
    
    def get_rating_stars(self, obj):
        """Отображение рейтинга в виде звезд"""
        return '★' * obj.rating
    get_rating_stars.short_description = "Рейтинг"
    
    def short_content(self, obj):
        """Сокращенный текст отзыва"""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    short_content.short_description = "Текст отзыва"
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем текущего пользователя как создателя отзыва"""
        if not change:  # Только при создании нового отзыва
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Ограничиваем выбор типов контента только для объектов клиник, реабилитационных центров и частных врачей"""
        if db_field.name == "content_type":
            kwargs["queryset"] = ContentType.objects.filter(
                model__in=['clinic', 'rehabcenter', 'privatedoctor'],
                app_label='facilities'
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

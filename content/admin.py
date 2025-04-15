from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Banner, SiteSettings

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'start_date', 'end_date', 'order']
    list_filter = ['is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    ordering = ['order', '-start_date']
    date_hierarchy = 'start_date'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'phone', 'email']
    search_fields = ['site_name', 'site_description']
    
    def has_add_permission(self, request):
        # Запрещаем создание новых записей, если уже есть одна
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

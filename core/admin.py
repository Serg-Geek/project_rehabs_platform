from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import City, Region, CityCoordinates

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'slug', 'is_active']
    list_filter = ['region', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CityCoordinates)
class CityCoordinatesAdmin(admin.ModelAdmin):
    list_display = ['city', 'region', 'coordinates_display', 'is_active']
    list_filter = ['is_active', 'city__region']
    search_fields = ['city__name']
    readonly_fields = ['region']
    
    fieldsets = (
        (None, {
            'fields': ('city', 'is_active'),
        }),
        ('Координаты', {
            'fields': ('latitude', 'longitude'),
            'description': format_html('''
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
                    <h4 style="margin-top: 0; color: #495057;">📍 Как получить координаты:</h4>
                    <ol style="margin-bottom: 0;">
                        <li>Откройте <a href="https://maps.google.com" target="_blank" style="color: #007bff;">Google Maps</a></li>
                        <li>Найдите нужный город</li>
                        <li>Правый клик на карте → "Что здесь?"</li>
                        <li>Скопируйте координаты (например: 55.7558, 37.6176)</li>
                    </ol>
                    <p style="margin: 10px 0 0 0; font-weight: bold; color: #495057;">
                        📋 Формат: Широта: 55.7558, Долгота: 37.6176
                    </p>
                </div>
            ''')
        }),
    )

    def region(self, obj):
        """Отображает регион города в списке"""
        return obj.city.region.name if obj.city and obj.city.region else '-'
    region.short_description = _('Регион')
    region.admin_order_field = 'city__region__name'

    def coordinates_display(self, obj):
        """Отображает координаты в удобном формате"""
        if obj.latitude and obj.longitude:
            return f"{obj.latitude}, {obj.longitude}"
        return '-'
    coordinates_display.short_description = _('Координаты')

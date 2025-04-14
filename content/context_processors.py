from django.utils import timezone
from .models import Banner, SiteSettings

def site_content(request):
    """Контекстный процессор для управления контентом сайта"""
    today = timezone.now().date()
    
    # Получаем активные баннеры
    banners = Banner.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).order_by('order')
    
    # Получаем настройки сайта
    try:
        site_settings = SiteSettings.objects.get()
    except SiteSettings.DoesNotExist:
        site_settings = None
    
    return {
        'banners': banners,
        'site_settings': site_settings
    } 
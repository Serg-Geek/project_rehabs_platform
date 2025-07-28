from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Banner
from django.utils import timezone

# Create your views here.

class HomeView(TemplateView):
    """
    Home page view with active banners.
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Add active banners to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with active banners
        """
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        banners = Banner.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).order_by('order')
        context['banners'] = banners
        return context

class BannerView(TemplateView):
    """
    Banner display view for homepage.
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Add active banners to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with active banners
        """
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Получаем все активные баннеры
        banners = Banner.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).order_by('order')
        
        context['banners'] = banners
        return context

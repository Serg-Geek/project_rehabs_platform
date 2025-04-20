from django.shortcuts import render
from django.views.generic import DetailView, TemplateView
from django.http import Http404
from .models import Banner, StaticPage
from django.utils import timezone

# Create your views here.

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        banners = Banner.objects.filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).order_by('order')
        context['banners'] = banners
        return context

class StaticPageView(DetailView):
    """Представление для отображения статической страницы"""
    model = StaticPage
    template_name = 'content/static_page.html'
    context_object_name = 'page'
    
    def get_object(self, queryset=None):
        """Получение объекта страницы с проверкой активности"""
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404("Страница не найдена или неактивна")
        return obj

class BannerView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
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

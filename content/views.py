from django.shortcuts import render
from django.views.generic import DetailView
from django.http import Http404
from .models import StaticPage

# Create your views here.

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

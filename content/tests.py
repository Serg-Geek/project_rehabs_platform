from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Banner, SiteSettings
from .context_processors import site_content

class ContextProcessorsTest(TestCase):
    """Тесты для контекст-процессоров"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        
        # Создаем активный баннер
        self.active_banner = Banner.objects.create(
            title='Активный баннер',
            description='Описание активного баннера',
            image='banners/active.jpg',
            link='https://example.com',
            is_active=True,
            order=1,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        # Создаем неактивный баннер
        self.inactive_banner = Banner.objects.create(
            title='Неактивный баннер',
            description='Описание неактивного баннера',
            image='banners/inactive.jpg',
            link='https://example.com',
            is_active=False,
            order=2,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        # Создаем настройки сайта
        self.settings = SiteSettings.objects.create(
            site_name='Тестовый сайт',
            site_description='Описание тестового сайта',
            phone='+7 (999) 999-99-99',
            email='test@example.com',
            address='Тестовый адрес',
            working_hours='Пн-Пт 9:00-18:00',
            social_media={'vk': 'https://vk.com/test', 'telegram': 'https://t.me/test'},
            seo_keywords='тест, ключевые слова',
            seo_description='Тестовое SEO описание'
        )
    
    def test_banners_context_processor(self):
        """Проверка контекст-процессора баннеров"""
        context = site_content(self.request)
        self.assertIn('banners', context)
        self.assertEqual(len(context['banners']), 1)  # Только активный баннер
        self.assertEqual(context['banners'][0], self.active_banner)
    
    def test_site_settings_context_processor(self):
        """Проверка контекст-процессора настроек сайта"""
        context = site_content(self.request)
        self.assertIn('site_settings', context)
        self.assertEqual(context['site_settings'], self.settings)

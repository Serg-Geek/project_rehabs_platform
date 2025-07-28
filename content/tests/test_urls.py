from django.test import TestCase
from django.urls import reverse, resolve
from content.views import BannerView


class ContentUrlsTest(TestCase):
    """Тесты для URL-ов content приложения"""
    
    def test_banner_url(self):
        """Тест URL для страницы баннеров"""
        url = reverse('content:banner')
        self.assertEqual(url, '/content/banner/')
    
    def test_banner_view_resolves(self):
        """Тест разрешения URL для BannerView"""
        resolver = resolve('/content/banner/')
        self.assertEqual(resolver.func.view_class, BannerView)
        self.assertEqual(resolver.namespace, 'content')
        self.assertEqual(resolver.url_name, 'banner')

    def test_banner_url_pattern(self):
        """Тест паттерна URL для баннеров"""
        from content.urls import urlpatterns
        
        # Проверяем, что есть URL для баннеров
        banner_urls = [url for url in urlpatterns if url.name == 'banner']
        self.assertEqual(len(banner_urls), 1)
        
        # Проверяем паттерн - исправляем под реальный формат Django
        banner_url = banner_urls[0]
        self.assertEqual(banner_url.pattern.regex.pattern, r'^banner/\Z')

    def test_content_app_namespace(self):
        """Тест namespace приложения content"""
        from content.urls import app_name
        self.assertEqual(app_name, 'content')

    def test_banner_url_with_namespace(self):
        """Тест URL с namespace"""
        url = reverse('content:banner')
        self.assertTrue(url.startswith('/content/'))
        self.assertTrue(url.endswith('/')) 
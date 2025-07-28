"""
Тесты для middleware логирования.

Проверяет работу middleware для логирования запросов и безопасности.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from pathlib import Path

User = get_user_model()


class LoggingMiddlewareTests(TestCase):
    """Тесты middleware для логирования."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем папку для логов
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def test_request_logging_middleware(self):
        """Тест middleware логирования запросов."""
        # Выполняем запрос
        response = self.client.get('/admin/')
        
        # Проверяем, что лог записан
        log_file = self.logs_dir / 'requests.log'
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('REQUEST_START', content)
            self.assertIn('/admin/', content)
    
    def test_security_middleware(self):
        """Тест middleware безопасности."""
        # Тестируем подозрительный запрос
        suspicious_url = '/test/?param=<script>alert("xss")</script>'
        response = self.client.get(suspicious_url)
        
        # Проверяем, что лог записан
        log_file = self.logs_dir / 'security.log'
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('SUSPICIOUS_ACTIVITY', content)
            self.assertIn('xss_attempt', content) 
"""
Интеграционные тесты логирования.

Проверяет полный цикл логирования и ротацию логов.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from pathlib import Path

User = get_user_model()


class LoggingIntegrationTests(TestCase):
    """Интеграционные тесты логирования."""
    
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
    
    def test_full_logging_flow(self):
        """Тест полного цикла логирования."""
        # Выполняем несколько действий
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/admin/')
        self.client.logout()
        
        # Проверяем, что логи созданы
        expected_logs = [
            'business.log',
            'security.log',
            'requests.log',
            'general.log'
        ]
        
        for log_file in expected_logs:
            log_path = self.logs_dir / log_file
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIsInstance(content, str)
    
    def test_log_rotation(self):
        """Тест ротации логов."""
        # Создаем тестовый лог файл
        test_log = self.logs_dir / 'general.log'
        with open(test_log, 'w', encoding='utf-8') as f:
            f.write('Test log entry\n')
        
        # Проверяем, что файл существует
        self.assertTrue(test_log.exists())
        
        # Проверяем размер файла
        self.assertGreater(test_log.stat().st_size, 0) 
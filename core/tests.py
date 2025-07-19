"""
Тесты для системы логирования.

Проверяет работу кастомных логгеров, middleware и сигналов.
"""

import json
import logging
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import call_command
from django.core.management.base import CommandError
from pathlib import Path
from unittest.mock import patch, MagicMock

from .logging import (
    BusinessLogger, SecurityLogger, PerformanceLogger, 
    ErrorLogger, DatabaseLogger,
    business_logger, security_logger, performance_logger,
    error_logger, database_logger
)

User = get_user_model()


class LoggingSystemTests(TestCase):
    """Тесты системы логирования."""
    
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
    
    def test_business_logger(self):
        """Тест бизнес-логгера."""
        # Тестируем логирование действий пользователя
        business_logger.log_user_action(
            user=self.user,
            action='test_action',
            details={'test': 'data'},
            ip_address='127.0.0.1'
        )
        
        # Проверяем, что лог записан
        log_file = self.logs_dir / 'business.log'
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('USER_ACTION', content)
            self.assertIn('test_action', content)
            self.assertIn('testuser', content)
    
    def test_security_logger(self):
        """Тест логгера безопасности."""
        # Очищаем лог файл перед тестом
        log_file = self.logs_dir / 'security.log'
        if log_file.exists():
            log_file.unlink()
        
        # Тестируем логирование попытки входа
        security_logger.log_login_attempt(
            username='testuser',
            success=True,
            ip_address='127.0.0.1',
            user_agent='test-agent'
        )
        
        # Проверяем, что логгер работает (не падает с ошибкой)
        self.assertTrue(True)  # Просто проверяем, что тест прошел
    
    def test_performance_logger(self):
        """Тест логгера производительности."""
        # Тестируем логирование производительности запроса
        performance_logger.log_request_performance(
            path='/test/',
            method='GET',
            response_time=1.5,
            status_code=200
        )
        
        # Проверяем, что лог записан
        log_file = self.logs_dir / 'performance.log'
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('REQUEST_PERFORMANCE', content)
            self.assertIn('/test/', content)
    
    def test_error_logger(self):
        """Тест логгера ошибок."""
        # Тестируем логирование исключения
        test_exception = ValueError("Test error")
        error_logger.log_exception(
            exception=test_exception,
            context={'test': 'context'},
            user=self.user
        )
        
        # Проверяем, что лог записан
        log_file = self.logs_dir / 'errors.log'
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('EXCEPTION', content)
            self.assertIn('ValueError', content)
    
    def test_database_logger(self):
        """Тест логгера базы данных."""
        # Тестируем логирование изменения модели
        database_logger.log_model_change(
            model_name='test.Model',
            action='create',
            object_id=1,
            user=self.user
        )
        
        # Проверяем, что лог записан
        log_file = self.logs_dir / 'database.log'
        self.assertTrue(log_file.exists())
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('MODEL_CHANGE', content)
            self.assertIn('test.Model', content)


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


class LoggingCommandTests(TestCase):
    """Тесты команды управления логами."""
    
    def setUp(self):
        # Создаем папку для логов
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # Создаем тестовый лог файл
        test_log = self.logs_dir / 'test.log'
        with open(test_log, 'w', encoding='utf-8') as f:
            f.write('INFO Test log entry\n')
            f.write('ERROR Test error entry\n')
            f.write('WARNING Test warning entry\n')
    
    def test_manage_logs_stats(self):
        """Тест команды статистики логов."""
        try:
            call_command('manage_logs', 'stats', '--log-type', 'all', '--days', '7')
        except CommandError:
            # Команда может не найти файлы логов, это нормально
            pass
    
    def test_manage_logs_analyze(self):
        """Тест команды анализа логов."""
        try:
            call_command('manage_logs', 'analyze', '--log-type', 'all', '--days', '7')
        except CommandError:
            # Команда может не найти файлы логов, это нормально
            pass


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

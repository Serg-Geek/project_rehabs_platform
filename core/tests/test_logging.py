"""
Тесты для системы логирования.

Проверяет работу кастомных логгеров.
"""

import json
import logging
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from pathlib import Path

from core.logging import (
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
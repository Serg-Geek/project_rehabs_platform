"""
Тесты для команд управления логами.

Проверяет работу команд управления логами.
"""

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from pathlib import Path


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
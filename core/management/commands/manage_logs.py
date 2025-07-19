"""
Команда для управления логами.

Предоставляет функции для:
- Просмотра статистики логов
- Очистки старых логов
- Анализа логов
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Управление логами системы'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['stats', 'clean', 'analyze', 'show'],
            help='Действие для выполнения'
        )
        parser.add_argument(
            '--log-type',
            choices=['all', 'errors', 'security', 'business', 'performance', 'database', 'requests'],
            default='all',
            help='Тип логов для обработки'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Количество дней для анализа'
        )

    def handle(self, *args, **options):
        action = options['action']
        log_type = options['log_type']
        days = options['days']

        logs_dir = Path(settings.BASE_DIR) / 'logs'
        
        if not logs_dir.exists():
            self.stdout.write(
                self.style.WARNING('Папка logs не существует. Создаю...')
            )
            logs_dir.mkdir(exist_ok=True)

        if action == 'stats':
            self.show_stats(logs_dir, log_type, days)
        elif action == 'clean':
            self.clean_logs(logs_dir, log_type, days)
        elif action == 'analyze':
            self.analyze_logs(logs_dir, log_type, days)
        elif action == 'show':
            self.show_logs(logs_dir, log_type, days)

    def show_stats(self, logs_dir, log_type, days):
        """Показать статистику логов."""
        self.stdout.write(self.style.SUCCESS(f'Статистика логов за последние {days} дней:'))
        
        log_files = self._get_log_files(logs_dir, log_type)
        
        for log_file in log_files:
            if log_file.exists():
                stats = self._analyze_log_file(log_file, days)
                self.stdout.write(f'\n{log_file.name}:')
                self.stdout.write(f'  Всего записей: {stats["total_lines"]}')
                self.stdout.write(f'  Уровень ERROR: {stats["error_count"]}')
                self.stdout.write(f'  Уровень WARNING: {stats["warning_count"]}')
                self.stdout.write(f'  Уровень INFO: {stats["info_count"]}')
                self.stdout.write(f'  Размер файла: {stats["file_size_mb"]:.2f} MB')

    def clean_logs(self, logs_dir, log_type, days):
        """Очистить старые логи."""
        cutoff_date = datetime.now() - timedelta(days=days)
        log_files = self._get_log_files(logs_dir, log_type)
        
        cleaned_count = 0
        for log_file in log_files:
            if log_file.exists():
                # Проверяем дату модификации файла
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_date:
                    log_file.unlink()
                    cleaned_count += 1
                    self.stdout.write(f'Удален: {log_file.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Очищено {cleaned_count} файлов логов')
        )

    def analyze_logs(self, logs_dir, log_type, days):
        """Анализ логов."""
        self.stdout.write(self.style.SUCCESS(f'Анализ логов за последние {days} дней:'))
        
        log_files = self._get_log_files(logs_dir, log_type)
        
        for log_file in log_files:
            if log_file.exists():
                analysis = self._detailed_analysis(log_file, days)
                self.stdout.write(f'\n{log_file.name}:')
                
                if analysis['top_errors']:
                    self.stdout.write('  Топ ошибок:')
                    for error, count in analysis['top_errors'][:5]:
                        self.stdout.write(f'    {error}: {count}')
                
                if analysis['top_ips']:
                    self.stdout.write('  Топ IP адресов:')
                    for ip, count in analysis['top_ips'][:5]:
                        self.stdout.write(f'    {ip}: {count}')

    def show_logs(self, logs_dir, log_type, days):
        """Показать содержимое логов."""
        log_files = self._get_log_files(logs_dir, log_type)
        
        for log_file in log_files:
            if log_file.exists():
                self.stdout.write(f'\n=== {log_file.name} ===')
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        # Показываем последние 50 строк
                        for line in lines[-50:]:
                            self.stdout.write(line.rstrip())
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка чтения файла {log_file}: {e}')
                    )

    def _get_log_files(self, logs_dir, log_type):
        """Получить список файлов логов."""
        if log_type == 'all':
            return [
                logs_dir / 'general.log',
                logs_dir / 'errors.log',
                logs_dir / 'security.log',
                logs_dir / 'business.log',
                logs_dir / 'performance.log',
                logs_dir / 'database.log',
                logs_dir / 'requests.log',
            ]
        else:
            return [logs_dir / f'{log_type}.log']

    def _analyze_log_file(self, log_file, days):
        """Анализ одного файла логов."""
        stats = {
            'total_lines': 0,
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'file_size_mb': 0,
        }
        
        if log_file.exists():
            stats['file_size_mb'] = log_file.stat().st_size / (1024 * 1024)
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        stats['total_lines'] += 1
                        if 'ERROR' in line:
                            stats['error_count'] += 1
                        elif 'WARNING' in line:
                            stats['warning_count'] += 1
                        elif 'INFO' in line:
                            stats['info_count'] += 1
            except Exception:
                pass
        
        return stats

    def _detailed_analysis(self, log_file, days):
        """Детальный анализ файла логов."""
        analysis = {
            'top_errors': [],
            'top_ips': [],
        }
        
        error_counts = {}
        ip_counts = {}
        
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        # Анализ ошибок
                        if 'ERROR' in line:
                            # Извлекаем тип ошибки
                            parts = line.split()
                            if len(parts) > 2:
                                error_type = parts[2]
                                error_counts[error_type] = error_counts.get(error_type, 0) + 1
                        
                        # Анализ IP адресов
                        if 'ip_address' in line:
                            try:
                                # Пытаемся извлечь IP из JSON
                                if '{' in line and '}' in line:
                                    json_start = line.find('{')
                                    json_end = line.rfind('}') + 1
                                    json_str = line[json_start:json_end]
                                    data = json.loads(json_str)
                                    ip = data.get('ip_address')
                                    if ip:
                                        ip_counts[ip] = ip_counts.get(ip, 0) + 1
                            except:
                                pass
            except Exception:
                pass
        
        analysis['top_errors'] = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        analysis['top_ips'] = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
        
        return analysis 
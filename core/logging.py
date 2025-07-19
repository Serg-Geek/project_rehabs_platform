"""
Кастомные логгеры для системы логирования.

Предоставляет специализированные логгеры для разных типов событий:
- Бизнес-логика
- Безопасность
- Производительность
- Ошибки
"""

import logging
import json
from datetime import datetime
from django.conf import settings
from django.utils import timezone


class BusinessLogger:
    """Логгер для бизнес-событий."""
    
    def __init__(self):
        self.logger = logging.getLogger('business')
    
    def log_user_action(self, user, action, details=None, ip_address=None):
        """Логирование действий пользователя."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user and user.is_authenticated else None,
            'username': user.username if user and user.is_authenticated else 'anonymous',
            'action': action,
            'details': details or {},
            'ip_address': ip_address,
        }
        self.logger.info(f"USER_ACTION: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_request_created(self, request_obj, user=None, ip_address=None):
        """Логирование создания заявки."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'request_id': request_obj.id,
            'request_type': request_obj.__class__.__name__,
            'user_id': user.id if user else None,
            'ip_address': ip_address,
            'status': request_obj.status,
        }
        self.logger.info(f"REQUEST_CREATED: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_payment_event(self, payment_data, user=None):
        """Логирование платежных событий."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'payment_id': payment_data.get('id'),
            'amount': payment_data.get('amount'),
            'currency': payment_data.get('currency'),
            'status': payment_data.get('status'),
            'user_id': user.id if user else None,
        }
        self.logger.info(f"PAYMENT_EVENT: {json.dumps(log_data, ensure_ascii=False)}")


class SecurityLogger:
    """Логгер для событий безопасности."""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_login_attempt(self, username, success, ip_address, user_agent=None):
        """Логирование попыток входа."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'username': username,
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        level = logging.INFO if success else logging.WARNING
        self.logger.log(level, f"LOGIN_ATTEMPT: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_suspicious_activity(self, activity_type, details, ip_address, user=None):
        """Логирование подозрительной активности."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'activity_type': activity_type,
            'details': details,
            'ip_address': ip_address,
            'user_id': user.id if user else None,
            'username': user.username if user else None,
        }
        self.logger.warning(f"SUSPICIOUS_ACTIVITY: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_permission_denied(self, user, action, resource, ip_address):
        """Логирование отказа в доступе."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user.is_authenticated else None,
            'username': user.username if user.is_authenticated else 'anonymous',
            'action': action,
            'resource': resource,
            'ip_address': ip_address,
        }
        self.logger.warning(f"PERMISSION_DENIED: {json.dumps(log_data, ensure_ascii=False)}")


class PerformanceLogger:
    """Логгер для событий производительности."""
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def log_slow_query(self, query, execution_time, threshold=1.0):
        """Логирование медленных запросов."""
        if execution_time > threshold:
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'query': str(query),
                'execution_time': execution_time,
                'threshold': threshold,
            }
            self.logger.warning(f"SLOW_QUERY: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_request_performance(self, path, method, response_time, status_code):
        """Логирование производительности запросов."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'path': path,
            'method': method,
            'response_time': response_time,
            'status_code': status_code,
        }
        self.logger.info(f"REQUEST_PERFORMANCE: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_memory_usage(self, memory_usage, threshold=100):
        """Логирование использования памяти."""
        if memory_usage > threshold:
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'memory_usage_mb': memory_usage,
                'threshold_mb': threshold,
            }
            self.logger.warning(f"HIGH_MEMORY_USAGE: {json.dumps(log_data, ensure_ascii=False)}")


class ErrorLogger:
    """Логгер для ошибок и исключений."""
    
    def __init__(self):
        self.logger = logging.getLogger('errors')
    
    def log_exception(self, exception, context=None, user=None):
        """Логирование исключений."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'context': context or {},
            'user_id': user.id if user else None,
            'username': user.username if user else None,
        }
        self.logger.error(f"EXCEPTION: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_http_error(self, status_code, path, method, user=None, ip_address=None):
        """Логирование HTTP ошибок."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'status_code': status_code,
            'path': path,
            'method': method,
            'user_id': user.id if user else None,
            'ip_address': ip_address,
        }
        level = logging.ERROR if status_code >= 500 else logging.WARNING
        self.logger.log(level, f"HTTP_ERROR: {json.dumps(log_data, ensure_ascii=False)}")


class DatabaseLogger:
    """Логгер для событий базы данных."""
    
    def __init__(self):
        self.logger = logging.getLogger('database')
    
    def log_model_change(self, model_name, action, object_id, user=None):
        """Логирование изменений моделей."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'model': model_name,
            'action': action,  # create, update, delete
            'object_id': object_id,
            'user_id': user.id if user else None,
            'username': user.username if user else None,
        }
        self.logger.info(f"MODEL_CHANGE: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_connection_error(self, error_message, database_name):
        """Логирование ошибок подключения к БД."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'error_message': error_message,
            'database': database_name,
        }
        self.logger.error(f"DB_CONNECTION_ERROR: {json.dumps(log_data, ensure_ascii=False)}")


# Создаем экземпляры логгеров для удобного использования
business_logger = BusinessLogger()
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()
error_logger = ErrorLogger()
database_logger = DatabaseLogger() 
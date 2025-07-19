"""
Middleware для автоматического логирования.

Предоставляет middleware для:
- Логирования всех HTTP запросов
- Измерения производительности
- Логирования ошибок
- Обнаружения подозрительной активности
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from django.core.exceptions import PermissionDenied
from .logging import performance_logger, error_logger, security_logger


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware для логирования HTTP запросов."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.logger = logging.getLogger('requests')
    
    def process_request(self, request):
        """Логирование входящих запросов."""
        request.start_time = time.time()
        
        # Логируем только важные запросы (исключаем статику и медиа)
        if not self._should_skip_logging(request.path):
            log_data = {
                'timestamp': time.time(),
                'method': request.method,
                'path': request.path,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'user_id': request.user.id if request.user.is_authenticated else None,
                'username': request.user.username if request.user.is_authenticated else 'anonymous',
            }
            self.logger.info(f"REQUEST_START: {log_data}")
    
    def process_response(self, request, response):
        """Логирование исходящих ответов."""
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            
            # Логируем производительность
            performance_logger.log_request_performance(
                path=request.path,
                method=request.method,
                response_time=response_time,
                status_code=response.status_code
            )
            
            # Логируем медленные запросы
            if response_time > 2.0:  # Запросы дольше 2 секунд
                log_data = {
                    'timestamp': time.time(),
                    'method': request.method,
                    'path': request.path,
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'ip_address': self._get_client_ip(request),
                }
                self.logger.warning(f"SLOW_REQUEST: {log_data}")
            
            # Логируем ошибки
            if response.status_code >= 400:
                error_logger.log_http_error(
                    status_code=response.status_code,
                    path=request.path,
                    method=request.method,
                    user=request.user,
                    ip_address=self._get_client_ip(request)
                )
        
        return response
    
    def process_exception(self, request, exception):
        """Логирование исключений."""
        if isinstance(exception, Http404):
            # 404 ошибки логируем как INFO
            log_data = {
                'timestamp': time.time(),
                'method': request.method,
                'path': request.path,
                'exception': 'Http404',
                'ip_address': self._get_client_ip(request),
            }
            self.logger.info(f"NOT_FOUND: {log_data}")
        elif isinstance(exception, PermissionDenied):
            # Отказы в доступе логируем как WARNING
            security_logger.log_permission_denied(
                user=request.user,
                action=request.method,
                resource=request.path,
                ip_address=self._get_client_ip(request)
            )
        else:
            # Остальные исключения логируем как ERROR
            error_logger.log_exception(
                exception=exception,
                context={
                    'method': request.method,
                    'path': request.path,
                    'ip_address': self._get_client_ip(request),
                },
                user=request.user
            )
    
    def _should_skip_logging(self, path):
        """Определяет, нужно ли пропустить логирование для данного пути."""
        skip_paths = [
            '/static/',
            '/media/',
            '/favicon.ico',
            '/robots.txt',
            '/admin/jsi18n/',
        ]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _get_client_ip(self, request):
        """Получение IP адреса клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityMiddleware(MiddlewareMixin):
    """Middleware для обнаружения подозрительной активности."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.logger = logging.getLogger('security')
    
    def process_request(self, request):
        """Проверка на подозрительную активность."""
        ip_address = self._get_client_ip(request)
        
        # Проверяем на SQL инъекции в URL
        suspicious_patterns = [
            'union select',
            'drop table',
            'delete from',
            'insert into',
            'update set',
            'script>',
            'javascript:',
        ]
        
        path_lower = request.path.lower()
        for pattern in suspicious_patterns:
            if pattern in path_lower:
                security_logger.log_suspicious_activity(
                    activity_type='sql_injection_attempt',
                    details={'pattern': pattern, 'path': request.path},
                    ip_address=ip_address,
                    user=request.user
                )
                break
        
        # Проверяем на XSS в параметрах
        for key, value in request.GET.items():
            if isinstance(value, str) and any(pattern in value.lower() for pattern in ['<script', 'javascript:']):
                security_logger.log_suspicious_activity(
                    activity_type='xss_attempt',
                    details={'parameter': key, 'value': value},
                    ip_address=ip_address,
                    user=request.user
                )
                break
    
    def _get_client_ip(self, request):
        """Получение IP адреса клиента."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DatabaseLoggingMiddleware(MiddlewareMixin):
    """Middleware для логирования операций с базой данных."""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.logger = logging.getLogger('database')
    
    def process_request(self, request):
        """Настройка логирования запросов к БД."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Добавляем информацию о пользователе в контекст
            request.db_user_context = {
                'user_id': request.user.id,
                'username': request.user.username,
            }
        return None 
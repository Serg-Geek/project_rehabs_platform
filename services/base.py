"""
Base service classes.

This module provides base classes for all services in the application.
"""

import logging
from typing import Any, Dict, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from .results import ServiceResult


class BaseService:
    """
    Base class for all services.
    
    Provides common functionality like logging, transaction management,
    and error handling for all service classes.
    """
    
    def __init__(self):
        """
        Initialize the service with a logger.
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    def log_info(self, message: str, **kwargs):
        """
        Log info message with additional context.
        
        Args:
            message: Message to log
            **kwargs: Additional context data
        """
        self.logger.info(f"{message} | {kwargs}")

    def log_error(self, message: str, error: Exception = None, **kwargs):
        """
        Log error message with exception and context.
        
        Args:
            message: Message to log
            error: Exception that occurred
            **kwargs: Additional context data
        """
        if error:
            self.logger.error(f"{message} | Error: {error} | {kwargs}", exc_info=True)
        else:
            self.logger.error(f"{message} | {kwargs}")

    def log_warning(self, message: str, **kwargs):
        """
        Log warning message with additional context.
        
        Args:
            message: Message to log
            **kwargs: Additional context data
        """
        self.logger.warning(f"{message} | {kwargs}")

    @transaction.atomic
    def execute_in_transaction(self, func, *args, **kwargs) -> ServiceResult:
        """
        Execute a function within a database transaction.
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            ServiceResult: Result of the operation
        """
        try:
            result = func(*args, **kwargs)
            return result
        except ValidationError as e:
            self.log_error("Validation error in transaction", e)
            return ServiceResult.error_result(
                error="Ошибка валидации данных",
                errors=e.message_dict if hasattr(e, 'message_dict') else None
            )
        except Exception as e:
            self.log_error("Unexpected error in transaction", e)
            return ServiceResult.error_result(
                error="Произошла непредвиденная ошибка"
            )

    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> ServiceResult:
        """
        Validate that required fields are present in data.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Returns:
            ServiceResult: Success if all fields present, error otherwise
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return ServiceResult.error_result(
                error=f"Отсутствуют обязательные поля: {', '.join(missing_fields)}",
                code="MISSING_FIELDS"
            )
        
        return ServiceResult.success_result()

    def safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Safely get value from dictionary with default.
        
        Args:
            data: Dictionary to get value from
            key: Key to look for
            default: Default value if key not found
            
        Returns:
            Value from dictionary or default
        """
        return data.get(key, default)

    def safe_get_int(self, data: Dict[str, Any], key: str, default: int = None) -> Optional[int]:
        """
        Safely get integer value from dictionary.
        
        Args:
            data: Dictionary to get value from
            key: Key to look for
            default: Default value if key not found or conversion fails
            
        Returns:
            Integer value or default
        """
        try:
            value = data.get(key)
            if value is not None:
                return int(value)
            return default
        except (ValueError, TypeError):
            return default

    def format_error_message(self, error: Exception) -> str:
        """
        Format error message for user display.
        
        Args:
            error: Exception to format
            
        Returns:
            str: Formatted error message
        """
        if hasattr(error, 'message_dict'):
            # Django validation error
            messages = []
            for field, errors in error.message_dict.items():
                if isinstance(errors, list):
                    messages.extend([f"{field}: {error}" for error in errors])
                else:
                    messages.append(f"{field}: {errors}")
            return "; ".join(messages)
        else:
            return str(error) 
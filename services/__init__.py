"""
Services layer for business logic.

This package contains service classes that handle business logic,
separating it from views and models.
"""

from .base import BaseService
from .results import ServiceResult

__all__ = ['BaseService', 'ServiceResult'] 
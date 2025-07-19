"""
Result objects for service layer.

This module provides standardized result objects for service methods
to ensure consistent return values and error handling.
"""

from dataclasses import dataclass
from typing import Any, Optional, Dict, List


@dataclass
class ServiceResult:
    """
    Standard result object for service methods.
    
    Attributes:
        success: Whether the operation was successful
        data: The result data (if successful)
        message: Success message
        error: Error message (if failed)
        errors: Dictionary of field-specific errors
        code: Optional error code
    """
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    errors: Optional[Dict[str, List[str]]] = None
    code: Optional[str] = None

    def __bool__(self):
        """Return success status for boolean operations."""
        return self.success

    @classmethod
    def success_result(cls, data=None, message=None):
        """Create a successful result."""
        return cls(success=True, data=data, message=message)

    @classmethod
    def error_result(cls, error, code=None, errors=None):
        """Create an error result."""
        return cls(success=False, error=error, code=code, errors=errors)


@dataclass
class PaginatedResult(ServiceResult):
    """
    Result object for paginated data.
    
    Attributes:
        page: Current page number
        total_pages: Total number of pages
        total_count: Total number of items
        has_next: Whether there's a next page
        has_previous: Whether there's a previous page
    """
    page: int = 1
    total_pages: int = 1
    total_count: int = 0
    has_next: bool = False
    has_previous: bool = False

    @classmethod
    def from_paginator(cls, paginator, page_obj, data=None, message=None):
        """Create paginated result from Django paginator."""
        return cls(
            success=True,
            data=data or list(page_obj),
            message=message,
            page=page_obj.number,
            total_pages=paginator.num_pages,
            total_count=paginator.count,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous()
        ) 
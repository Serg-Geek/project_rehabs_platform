"""
Base mixins for views.

This module provides reusable mixins for common view functionality
like search, filtering, and pagination.
"""

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _


class SearchMixin:
    """
    Mixin for adding search functionality to views.
    
    Attributes:
        search_fields: List of model fields to search in
        search_param: GET parameter name for search query
        search_lookup: Lookup type for search (default: 'icontains')
    """
    
    search_fields = []
    search_param = 'search'
    search_lookup = 'icontains'
    
    def get_search_query(self):
        """Get search query from request."""
        return self.request.GET.get(self.search_param, '').strip()
    
    def get_queryset(self):
        """Add search filtering to queryset."""
        queryset = super().get_queryset()
        search_query = self.get_search_query()
        
        if search_query and self.search_fields:
            q_objects = Q()
            for field in self.search_fields:
                lookup = f"{field}__{self.search_lookup}"
                q_objects |= Q(**{lookup: search_query})
            queryset = queryset.filter(q_objects)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.get_search_query()
        return context


class FilterMixin:
    """
    Mixin for adding filtering functionality to views.
    
    Attributes:
        filter_fields: Dictionary mapping GET parameters to model fields
        filter_lookup: Default lookup type for filters (default: 'exact')
    """
    
    filter_fields = {}
    filter_lookup = 'exact'
    
    def get_filter_params(self):
        """Get filter parameters from request."""
        filters = {}
        for param, field in self.filter_fields.items():
            value = self.request.GET.get(param)
            if value:
                filters[field] = value
        return filters
    
    def get_queryset(self):
        """Add filtering to queryset."""
        queryset = super().get_queryset()
        filters = self.get_filter_params()
        
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter parameters to context."""
        context = super().get_context_data(**kwargs)
        context['filter_params'] = self.get_filter_params()
        return context


class OrderingMixin:
    """
    Mixin for adding ordering functionality to views.
    
    Attributes:
        ordering_fields: List of allowed ordering fields
        default_ordering: Default ordering field
        ordering_param: GET parameter name for ordering
    """
    
    ordering_fields = []
    default_ordering = None
    ordering_param = 'ordering'
    
    def get_ordering(self):
        """Get ordering from request or use default."""
        ordering = self.request.GET.get(self.ordering_param, self.default_ordering)
        
        if ordering and ordering in self.ordering_fields:
            return ordering
            
        return self.default_ordering
    
    def get_queryset(self):
        """Add ordering to queryset."""
        queryset = super().get_queryset()
        ordering = self.get_ordering()
        
        if ordering:
            queryset = queryset.order_by(ordering)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add ordering to context."""
        context = super().get_context_data(**kwargs)
        context['current_ordering'] = self.get_ordering()
        context['ordering_fields'] = self.ordering_fields
        return context


class PaginationMixin:
    """
    Mixin for adding pagination functionality to views.
    
    Attributes:
        paginate_by: Number of items per page
        page_param: GET parameter name for page number
    """
    
    paginate_by = 20
    page_param = 'page'
    
    def get_paginate_by(self):
        """Get number of items per page."""
        return self.paginate_by
    
    def get_page_number(self):
        """Get current page number from request."""
        return self.request.GET.get(self.page_param, 1)
    
    def paginate_queryset(self, queryset):
        """Paginate the queryset."""
        paginator = Paginator(queryset, self.get_paginate_by())
        page_number = self.get_page_number()
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
            
        return paginator, page_obj
    
    def get_context_data(self, **kwargs):
        """Add pagination data to context."""
        context = super().get_context_data(**kwargs)
        
        if hasattr(self, 'paginator') and hasattr(self, 'page_obj'):
            context.update({
                'paginator': self.paginator,
                'page_obj': self.page_obj,
                'is_paginated': self.paginator.num_pages > 1,
            })
            
        return context


class CacheMixin:
    """
    Mixin for adding caching functionality to views.
    
    Attributes:
        cache_timeout: Cache timeout in seconds
        cache_key_prefix: Prefix for cache keys
    """
    
    cache_timeout = 300  # 5 minutes
    cache_key_prefix = 'view_cache'
    
    def get_cache_key(self):
        """Generate cache key for this view."""
        # Include user ID if authenticated
        user_id = self.request.user.id if self.request.user.is_authenticated else 'anonymous'
        
        # Include query parameters
        query_params = self.request.GET.urlencode()
        
        return f"{self.cache_key_prefix}:{self.__class__.__name__}:{user_id}:{query_params}"
    
    def get_cached_data(self):
        """Get data from cache."""
        from django.core.cache import cache
        cache_key = self.get_cache_key()
        return cache.get(cache_key)
    
    def set_cached_data(self, data):
        """Set data in cache."""
        from django.core.cache import cache
        cache_key = self.get_cache_key()
        cache.set(cache_key, data, self.cache_timeout)
    
    def get_context_data(self, **kwargs):
        """Add cache information to context."""
        context = super().get_context_data(**kwargs)
        context['cache_key'] = self.get_cache_key()
        return context


class PermissionMixin:
    """
    Mixin for adding permission checking functionality to views.
    
    Attributes:
        required_permissions: List of required permissions
        permission_denied_message: Message to show when permission denied
    """
    
    required_permissions = []
    permission_denied_message = _("У вас нет прав для выполнения этого действия.")
    
    def has_permissions(self):
        """Check if user has required permissions."""
        if not self.required_permissions:
            return True
            
        if not self.request.user.is_authenticated:
            return False
            
        return all(
            self.request.user.has_perm(permission)
            for permission in self.required_permissions
        )
    
    def dispatch(self, request, *args, **kwargs):
        """Check permissions before processing request."""
        if not self.has_permissions():
            from django.contrib import messages
            from django.shortcuts import redirect
            
            messages.error(request, self.permission_denied_message)
            return redirect('home')  # Redirect to home or login
            
        return super().dispatch(request, *args, **kwargs) 
"""
Base mixins for views.

This module provides reusable mixins for common view functionality
like search, filtering, and pagination.
"""

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from core.models import City, Region


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
        page_kwarg: URL parameter name for page number
        allow_empty: Whether to allow empty pages
    """
    
    paginate_by = 20
    page_kwarg = 'page'
    allow_empty = True
    
    def get_paginate_by(self, queryset):
        """Get the number of items to paginate by."""
        return self.paginate_by
    
    def get_page_kwarg(self):
        """Get the URL parameter name for page number."""
        return self.page_kwarg
    
    def get_allow_empty(self):
        """Get whether to allow empty pages."""
        return self.allow_empty
    
    def paginate_queryset(self, queryset, page_size):
        """Paginate the queryset."""
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        
        paginator = Paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.get_page_kwarg()
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        
        try:
            page_number = int(page)
        except (ValueError, TypeError):
            page_number = 1
        
        try:
            page_obj = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.page(1)
        
        # Return 4 values as expected by Django ListView
        return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()
    
    def get_context_data(self, **kwargs):
        """Add pagination data to context."""
        context = super().get_context_data(**kwargs)
        
        if hasattr(self, 'object_list'):
            queryset = self.object_list
        else:
            queryset = self.get_queryset()
        
        page_size = self.get_paginate_by(queryset)
        paginator, page_obj, object_list, is_paginated = self.paginate_queryset(queryset, page_size)
        
        context.update({
            'paginator': paginator,
            'page_obj': page_obj,
            'is_paginated': is_paginated,
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


class GeoDataMixin:
    """
    Миксин для добавления гео-данных в контекст представлений
    """
    
    def get_geo_data(self, facility=None):
        """
        Получает гео-данные для учреждения или возвращает дефолтные
        
        Args:
            facility: Объект учреждения (Clinic, RehabCenter, PrivateDoctor) или специалиста (FacilitySpecialist)
            
        Returns:
            dict: Гео-данные для мета-тегов
        """
        # Если передан специалист, получаем учреждение через связь
        if facility and hasattr(facility, 'facility') and facility.facility:
            facility = facility.facility
        
        if facility and hasattr(facility, 'city') and facility.city:
            city = facility.city
            region = city.region
            
            return {
                'geo_region': 'RU',
                'geo_placename': f"{city.name}, {region.name}",
                'geo_position': self._get_coordinates_for_city(city),
                'icbm': self._get_coordinates_for_city(city),
                'city_name': city.name,
                'region_name': region.name,
                'full_location': f"{city.name}, {region.name}"
            }
        
        # Дефолтные значения для России
        return {
            'geo_region': 'RU',
            'geo_placename': 'Россия',
            'geo_position': '65.0000;105.0000',
            'icbm': '65.0000, 105.0000',
            'city_name': 'Анапа',
            'region_name': 'Краснодарский край',
            'full_location': 'Анапа, Краснодарский край'
        }
    
    def _get_coordinates_for_city(self, city):
        """
        Возвращает координаты для города
        В будущем можно вынести в отдельную модель с координатами
        
        Args:
            city: Объект города
            
        Returns:
            str: Координаты в формате "lat;lng"
        """
        # Координаты основных городов
        city_coordinates = {
            'Москва': '55.7558;37.6176',
            'Санкт-Петербург': '59.9311;30.3609',
            'Новосибирск': '55.0084;82.9357',
            'Екатеринбург': '56.8431;60.6454',
            'Казань': '55.8304;49.0661',
            'Сочи': '43.6028;39.7342',
            'Анапа': '44.8947;37.3166',
            'Краснодар': '45.0448;38.9760',
            'Химки': '55.8970;37.4297',
            'Подольск': '55.4289;37.5444',
            'Пушкин': '59.7231;30.4085',
            'Петергоф': '59.8850;29.9086',
            'Бердск': '54.7584;83.1072',
            'Нижний Тагил': '57.9194;59.9651',
            'Набережные Челны': '55.7436;52.3958',
        }
        
        return city_coordinates.get(city.name, '65.0000;105.0000')
    
    def get_context_data(self, **kwargs):
        """
        Добавляет гео-данные в контекст
        """
        context = super().get_context_data(**kwargs)
        
        # Получаем объект учреждения или специалиста из контекста или из self.object
        facility = context.get('facility') or context.get('specialist') or getattr(self, 'object', None)
        
        # Добавляем гео-данные
        geo_data = self.get_geo_data(facility)
        context.update(geo_data)
        
        return context 
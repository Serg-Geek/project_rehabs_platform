"""
Base mixins for views.

This module provides reusable mixins for common view functionality
like search, filtering, and pagination.
"""

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from core.models import City, Region, CityCoordinates


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
        """
        Get search query from request.
        
        Returns:
            str: Search query from GET parameters, stripped of whitespace
        """
        return self.request.GET.get(self.search_param, '').strip()
    
    def get_queryset(self):
        """
        Add search filtering to queryset.
        
        Returns:
            QuerySet: Filtered queryset based on search query
        """
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
        """
        Add search query to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with search query added
        """
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
        """
        Get filter parameters from request.
        
        Returns:
            dict: Dictionary of field-value pairs for filtering
        """
        filters = {}
        for param, field in self.filter_fields.items():
            value = self.request.GET.get(param)
            if value:
                filters[field] = value
        return filters
    
    def get_queryset(self):
        """
        Add filtering to queryset.
        
        Returns:
            QuerySet: Filtered queryset based on GET parameters
        """
        queryset = super().get_queryset()
        filters = self.get_filter_params()
        
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add filter parameters to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with filter parameters added
        """
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
        """
        Get ordering from request or use default.
        
        Returns:
            str: Ordering field name or default ordering
        """
        ordering = self.request.GET.get(self.ordering_param, self.default_ordering)
        
        if ordering and ordering in self.ordering_fields:
            return ordering
            
        return self.default_ordering
    
    def get_queryset(self):
        """
        Add ordering to queryset.
        
        Returns:
            QuerySet: Ordered queryset
        """
        queryset = super().get_queryset()
        ordering = self.get_ordering()
        
        if ordering:
            queryset = queryset.order_by(ordering)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add ordering to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with ordering information added
        """
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
        """
        Get the number of items to paginate by.
        
        Args:
            queryset: The queryset to be paginated
            
        Returns:
            int: Number of items per page
        """
        return self.paginate_by
    
    def get_page_kwarg(self):
        """
        Get the URL parameter name for page number.
        
        Returns:
            str: URL parameter name for page number
        """
        return self.page_kwarg
    
    def get_allow_empty(self):
        """
        Get whether to allow empty pages.
        
        Returns:
            bool: True if empty pages are allowed
        """
        return self.allow_empty
    
    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset.
        
        Args:
            queryset: The queryset to paginate
            page_size: Number of items per page
            
        Returns:
            tuple: (paginator, page_obj, object_list, is_paginated)
        """
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
        """
        Add pagination data to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with pagination information added
        """
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
        """
        Generate cache key for this view.
        
        Returns:
            str: Unique cache key for this view instance
        """
        # Include user ID if authenticated
        user_id = self.request.user.id if self.request.user.is_authenticated else 'anonymous'
        
        # Include query parameters
        query_params = self.request.GET.urlencode()
        
        return f"{self.cache_key_prefix}:{self.__class__.__name__}:{user_id}:{query_params}"
    
    def get_cached_data(self):
        """
        Get data from cache.
        
        Returns:
            Any: Cached data or None if not found
        """
        from django.core.cache import cache
        cache_key = self.get_cache_key()
        return cache.get(cache_key)
    
    def set_cached_data(self, data):
        """
        Set data in cache.
        
        Args:
            data: Data to cache
        """
        from django.core.cache import cache
        cache_key = self.get_cache_key()
        cache.set(cache_key, data, self.cache_timeout)
    
    def get_context_data(self, **kwargs):
        """
        Add cache information to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with cache key added
        """
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
        """
        Check if user has required permissions.
        
        Returns:
            bool: True if user has all required permissions
        """
        if not self.required_permissions:
            return True
            
        if not self.request.user.is_authenticated:
            return False
            
        return all(
            self.request.user.has_perm(permission)
            for permission in self.required_permissions
        )
    
    def dispatch(self, request, *args, **kwargs):
        """
        Check permissions before processing request.
        
        Args:
            request: HTTP request object
            *args: Additional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            HttpResponse: Response object or redirect if permission denied
        """
        if not self.has_permissions():
            from django.contrib import messages
            from django.shortcuts import redirect
            
            messages.error(request, self.permission_denied_message)
            return redirect('home')  # Redirect to home or login
            
        return super().dispatch(request, *args, **kwargs) 


class GeoDataMixin:
    """
    Mixin for adding geographical data to view context.
    Used for facilities and staff.
    """
    
    def get_geo_data(self, facility=None):
        """
        Get geographical data for facility or specialist.
        
        Args:
            facility: Facility or specialist object
            
        Returns:
            dict: Dictionary with geographical data
        """
        # Если передан специалист, получаем учреждение через связь
        if facility and hasattr(facility, 'facility') and facility.facility:
            facility = facility.facility
        
        # Получаем город учреждения
        city = None
        if facility and hasattr(facility, 'city') and facility.city:
            city = facility.city
        
        # Если есть город, пытаемся получить координаты из БД
        if city:
            try:
                coords = CityCoordinates.objects.get(city=city, is_active=True)
                return {
                    'geo_region': 'RU',
                    'geo_placename': city.name,
                    'geo_position': coords.get_coordinates_string(),
                    'icbm': coords.get_icbm_string(),
                    'city_name': city.name,
                    'region_name': city.region.name if city.region else 'Россия',
                    'full_location': f"{city.name}, {city.region.name}" if city.region else city.name
                }
            except CityCoordinates.DoesNotExist:
                # Если координат нет в БД, используем хардкод для основных городов
                return self._get_coordinates_for_city(city.name)
        
        # Если нет города или координат, возвращаем данные по умолчанию
        return {
            'geo_region': 'RU',
            'geo_placename': 'Россия',
            'geo_position': '65.0000;105.0000',
            'icbm': '65.0000, 105.0000',
            'city_name': 'Анапа',
            'region_name': 'Краснодарский край',
            'full_location': 'Анапа, Краснодарский край'
        }
    
    def _get_coordinates_for_city(self, city_name):
        """
        Return coordinates for major cities (hardcoded as fallback).
        
        Args:
            city_name: Name of the city
            
        Returns:
            dict: Dictionary with geographical data for the city
        """
        coordinates = {
            'Москва': (55.7558, 37.6176),
            'Санкт-Петербург': (59.9311, 30.3609),
            'Новосибирск': (55.0084, 82.9357),
            'Екатеринбург': (56.8519, 60.6122),
            'Казань': (55.8304, 49.0661),
            'Нижний Новгород': (56.2965, 43.9361),
            'Челябинск': (55.1644, 61.4368),
            'Самара': (53.2001, 50.1500),
            'Уфа': (54.7388, 55.9721),
            'Ростов-на-Дону': (47.2357, 39.7015),
            'Краснодар': (45.0355, 38.9753),
            'Анапа': (44.8947, 37.3166),
            'Сочи': (43.6028, 39.7342),
            'Волгоград': (48.7080, 44.5133),
            'Пермь': (58.0105, 56.2502),
            'Воронеж': (51.6720, 39.1843),
            'Саратов': (51.5924, 46.0347),
            'Тольятти': (53.5078, 49.4204),
            'Ижевск': (56.8519, 53.2324),
            'Ульяновск': (54.3176, 48.3706),
            'Барнаул': (53.3548, 83.7698),
            'Иркутск': (52.2896, 104.2806),
            'Хабаровск': (48.4802, 135.0719),
            'Ярославль': (57.6261, 39.8875),
            'Владивосток': (43.1198, 131.8869),
            'Махачкала': (42.9849, 47.5047),
            'Томск': (56.4977, 84.9744),
            'Оренбург': (51.7727, 55.0988),
            'Кемерово': (55.3904, 86.0468),
            'Новокузнецк': (53.7945, 87.1848),
            'Рязань': (54.6269, 39.6916),
            'Астрахань': (46.3589, 48.0506),
            'Набережные Челны': (55.7436, 52.3958),
            'Пенза': (53.2007, 45.0046),
            'Липецк': (52.6031, 39.5708),
            'Киров': (58.6035, 49.6668),
            'Чебоксары': (56.1322, 47.2519),
            'Тула': (54.1961, 37.6182),
            'Калининград': (54.7074, 20.5072),
            'Курск': (51.7373, 36.1873),
            'Улан-Удэ': (51.8335, 107.5841),
            'Ставрополь': (45.0428, 41.9734),
            'Магнитогорск': (53.4186, 59.0472),
            'Иваново': (57.0004, 40.9739),
            'Брянск': (53.2521, 34.3717),
            'Тверь': (56.8587, 35.9006),
            'Белгород': (50.5977, 36.5858),
            'Архангельск': (64.5473, 40.5602),
            'Владимир': (56.1296, 40.4066),
            'Севастополь': (44.6166, 33.5254),
            'Чита': (52.0515, 113.4719),
            'Грозный': (43.3178, 45.6949),
            'Симферополь': (44.9572, 34.1108),
        }
        
        if city_name in coordinates:
            lat, lng = coordinates[city_name]
            return {
                'geo_region': 'RU',
                'geo_placename': city_name,
                'geo_position': f"{lat};{lng}",
                'icbm': f"{lat}, {lng}",
                'city_name': city_name,
                'region_name': 'Россия',
                'full_location': city_name
            }
        
        # Если город не найден, возвращаем данные по умолчанию
        return {
            'geo_region': 'RU',
            'geo_placename': 'Россия',
            'geo_position': '65.0000;105.0000',
            'icbm': '65.0000, 105.0000',
            'city_name': 'Анапа',
            'region_name': 'Краснодарский край',
            'full_location': 'Анапа, Краснодарский край'
        }
    
    def get_context_data(self, **kwargs):
        """
        Add geographical data to view context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with geographical data added
        """
        context = super().get_context_data(**kwargs)
        
        # Получаем объект учреждения или специалиста из контекста или self.object
        facility = context.get('facility') or context.get('specialist') or getattr(self, 'object', None)
        
        # Получаем географические данные
        geo_data = self.get_geo_data(facility)
        context.update(geo_data)
        
        return context 
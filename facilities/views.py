from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q, Exists, OuterRef
from .models import Clinic, RehabCenter, PrivateDoctor
from medical_services.models import FacilityService, Service
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import models
from core.mixins import SearchMixin, FilterMixin, PaginationMixin, CacheMixin, GeoDataMixin

# Create your views here.

class FacilityListView(ListView):
    """
    General list of all facilities.
    
    TODO: Refactor to use custom managers.
    """
    template_name = 'facilities/facility_list.html'
    context_object_name = 'facilities'
    paginate_by = 12

    def get_queryset(self):
        """
        Get combined queryset of clinics and rehabilitation centers.
        
        Returns:
            list: Combined list of clinics and rehabilitation centers
        """
        # Объединяем клиники и реабилитационные центры
        clinics = Clinic.objects.all()
        rehab_centers = RehabCenter.objects.all()
        return list(clinics) + list(rehab_centers)

class ClinicListView(SearchMixin, PaginationMixin, ListView):
    """
    List of clinics with search and pagination.
    
    Uses custom ClinicManager for query optimization.
    """
    model = Clinic
    template_name = 'facilities/clinic_list.html'
    context_object_name = 'clinics'
    paginate_by = 12
    
    # Настройки поиска
    search_fields = ['name', 'description', 'address']
    search_param = 'search'

    def get_queryset(self):
        """
        Use custom manager for optimization.
        
        Returns:
            QuerySet: Optimized queryset with related data
        """
        queryset = Clinic.objects.with_related_data()
        
        # Применяем поиск из миксина
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        """
        Add SEO context to the view.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with SEO metadata added
        """
        context = super().get_context_data(**kwargs)
        
        # SEO контекст
        context['meta_title'] = 'Клиники лечения зависимостей - Центр помощи зависимым'
        context['meta_description'] = 'Найдите лучшие клиники для лечения алкоголизма, наркомании и игромании по всей России. Профессиональная помощь, анонимно, 24/7.'
        
        return context

class RehabilitationCenterListView(SearchMixin, PaginationMixin, ListView):
    """
    List of rehabilitation centers with search and pagination.
    
    Uses custom RehabCenterManager for query optimization.
    """
    model = RehabCenter
    template_name = 'facilities/rehabilitation_list.html'
    context_object_name = 'rehabilitation_centers'
    paginate_by = 12
    
    # Настройки поиска
    search_fields = ['name', 'description', 'address']
    search_param = 'search'

    def get_queryset(self):
        """
        Use custom manager for optimization with program sorting.
        
        Returns:
            QuerySet: Optimized queryset with related data and optional sorting
        """
        queryset = RehabCenter.objects.with_related_data()
        sort = self.request.GET.get('sort')
        if sort == 'programs':
            ct = ContentType.objects.get_for_model(RehabCenter)
            program_services = FacilityService.objects.filter(
                content_type=ct,
                object_id=OuterRef('pk'),
                service__is_rehabilitation_program=True
            )
            queryset = queryset.annotate(
                has_program=Exists(program_services)
            ).order_by('-has_program', 'name')
        return super().get_queryset() if not sort else queryset

    def get_context_data(self, **kwargs):
        """
        Add SEO context to the view.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with SEO metadata added
        """
        context = super().get_context_data(**kwargs)
        
        # SEO контекст
        context['meta_title'] = 'Реабилитационные центры - Центр помощи зависимым'
        context['meta_description'] = 'Реабилитационные центры для лечения зависимостей по всей России. Программы реабилитации, детоксикация, ресоциализация. Анонимно.'
        
        return context

class FacilityDetailView(GeoDataMixin, DetailView):
    """
    Detailed view of a facility.
    
    Supports different facility types (clinics, rehabilitation centers).
    """
    context_object_name = 'facility'

    def get_model(self):
        """
        Get the model class based on facility type.
        
        Returns:
            Model: Clinic or RehabCenter model class
            
        Raises:
            ValueError: If facility type is invalid
        """
        facility_type = self.kwargs.get('facility_type')
        if facility_type == 'clinic':
            return Clinic
        elif facility_type == 'rehab':
            return RehabCenter
        raise ValueError("Invalid facility type")

    def get_template_name(self):
        """
        Get template name based on facility type.
        
        Returns:
            str: Template name for the facility type
            
        Raises:
            ValueError: If facility type is invalid
        """
        facility_type = self.kwargs.get('facility_type')
        if facility_type == 'clinic':
            return 'facilities/clinic_detail.html'
        elif facility_type == 'rehab':
            return 'facilities/rehabcenter_detail.html'
        raise ValueError("Invalid facility type")

    def get_queryset(self):
        """
        Use custom manager for optimization.
        
        Returns:
            QuerySet: Optimized queryset with full data
        """
        model = self.get_model()
        if model == Clinic:
            return Clinic.objects.with_full_data()
        elif model == RehabCenter:
            return RehabCenter.objects.with_full_data()
        return model.objects.all()

    def get_context_data(self, **kwargs):
        """
        Add facility-specific context data.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with facility data, services, and related facilities
        """
        context = super().get_context_data(**kwargs)
        model = self.get_model()
        
        # Получаем связанные учреждения
        related_facilities = self._get_related_facilities(model)
        
        # Получаем услуги учреждения
        services = self._get_facility_services()
        # Получаем реабилитационные программы
        programs = [fs for fs in services if getattr(fs.service, 'is_rehabilitation_program', False)]
        
        # Добавляем данные в контекст
        if isinstance(self.object, Clinic):
            context['clinic'] = self.object
        elif isinstance(self.object, RehabCenter):
            context['center'] = self.object
        
        context['related_facilities'] = related_facilities
        context['services'] = services
        context['programs'] = programs
        context['facility_type'] = self.kwargs.get('facility_type')
        
        # Добавляем from_service_obj для хлебных крошек
        from_service_slug = self.request.GET.get('from_service')
        if from_service_slug:
            try:
                from_service_obj = Service.objects.get(slug=from_service_slug)
                context['from_service_obj'] = from_service_obj
            except Service.DoesNotExist:
                pass
        
        return context

    def _get_related_facilities(self, model):
        """
        Get related facilities of the same type.
        
        Args:
            model: Model class (Clinic or RehabCenter)
            
        Returns:
            QuerySet: Related facilities
        """
        if model == Clinic:
            return Clinic.objects.filter(city=self.object.city).exclude(pk=self.object.pk)[:3]
        elif model == RehabCenter:
            return RehabCenter.objects.filter(city=self.object.city).exclude(pk=self.object.pk)[:3]
        return model.objects.none()

    def _get_facility_services(self):
        """
        Get services provided by the facility.
        
        Returns:
            list: List of active facility services
        """
        ct = ContentType.objects.get_for_model(self.object)
        return FacilityService.objects.filter(
            content_type=ct,
            object_id=self.object.pk,
            is_active=True
        ).select_related('service')

def load_more_rehabs(request):
    """
    AJAX loading of additional rehabilitation centers.
    
    TODO: Refactor to use custom manager.
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: JSON response with cards HTML and has_more flag
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = 12
        
        rehabs = RehabCenter.objects.all().order_by('id')[offset:offset + limit + 1]
        has_more = len(rehabs) > limit
        rehabs = rehabs[:limit]
        
        cards_html = ''
        for center in rehabs:
            cards_html += render_to_string(
                'includes/cards/rehab_card.html',
                {'facility': center},
                request=request
            )
        
        return JsonResponse({
            'cards': cards_html,
            'has_more': has_more
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def load_more_clinics(request):
    """
    AJAX loading of additional clinics.
    
    TODO: Refactor to use custom manager.
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: JSON response with cards HTML and has_more flag
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = 12
        
        clinics = Clinic.objects.all().order_by('id')[offset:offset + limit + 1]
        has_more = len(clinics) > limit
        clinics = clinics[:limit]
        
        cards_html = ''
        for clinic in clinics:
            cards_html += render_to_string(
                'includes/cards/clinic_card.html',
                {'clinic': clinic},
                request=request
            )
        
        return JsonResponse({
            'cards': cards_html,
            'has_more': has_more
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class PrivateDoctorListView(SearchMixin, FilterMixin, PaginationMixin, ListView):
    """
    List of private doctors with search, filtering and pagination.
    
    Uses custom PrivateDoctorManager for query optimization.
    """
    model = PrivateDoctor
    template_name = 'facilities/private_doctors_list.html'
    context_object_name = 'doctors'
    paginate_by = 12
    
    # Настройки поиска
    search_fields = ['first_name', 'last_name', 'middle_name', 'specializations__name', 'city__name']
    search_param = 'search'
    
    # Настройки фильтрации
    filter_fields = {
        'city': 'city__slug',
        'specialization': 'specializations__slug',
        'home_visits': 'home_visits'
    }

    def get_queryset(self):
        """
        Use custom manager for optimization.
        
        Returns:
            QuerySet: Optimized queryset with related data
        """
        queryset = PrivateDoctor.objects.with_related_data()
        
        # Применяем фильтры из миксинов
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        """
        Add filter context and SEO data to the view.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with filters, specializations and SEO metadata
        """
        context = super().get_context_data(**kwargs)
        
        # Добавляем фильтры в контекст
        context['search_query'] = self.request.GET.get('search', '')
        context['city_filter'] = self.request.GET.get('city', '')
        context['specialization_filter'] = self.request.GET.get('specialization', '')
        context['home_visits_filter'] = self.request.GET.get('home_visits', '')
        
        # Добавляем список всех специализаций для фильтра
        from staff.models import Specialization
        context['specializations'] = Specialization.objects.all().order_by('name')
        
        # SEO контекст
        context['meta_title'] = 'Частные врачи - Центр помощи зависимым'
        context['meta_description'] = 'Частные врачи-наркологи по всей России. Индивидуальный подход, выезд на дом, анонимное лечение зависимостей.'
        
        return context

class PrivateDoctorDetailView(GeoDataMixin, DetailView):
    """
    Detailed view of a private doctor.
    
    Uses custom manager for query optimization.
    """
    model = PrivateDoctor
    template_name = 'facilities/private_doctor_detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        """
        Use custom manager for optimization.
        
        Returns:
            QuerySet: Optimized queryset with full data
        """
        return PrivateDoctor.objects.with_full_data()

    def get_context_data(self, **kwargs):
        """
        Add doctor-specific context data.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with related doctors, services and SEO metadata
        """
        context = super().get_context_data(**kwargs)
        
        # Получаем связанных врачей
        related_doctors = self._get_related_doctors()
        
        # Получаем услуги врача
        services = self._get_doctor_services()
        
        # Получаем отзывы врача
        reviews = self._get_doctor_reviews()
        
        context['related_doctors'] = related_doctors
        context['services'] = services
        context['reviews'] = reviews
        
        # SEO
        context['meta_title'] = self.object.meta_title or self.object.get_full_name()
        context['meta_description'] = self.object.meta_description or (self.object.biography[:160] if self.object.biography else '')
        context['meta_keywords'] = self.object.meta_keywords
        context['meta_image'] = self.object.meta_image.url if self.object.meta_image else None
        return context
    
    def _get_related_doctors(self):
        """
        Get related doctors with similar specializations or location.
        
        Returns:
            QuerySet: Related doctors
        """
        related_doctors = PrivateDoctor.objects.filter(is_active=True)
        
        # Фильтруем по специализации
        if self.object.specializations.exists():
            related_doctors = related_doctors.filter(
                specializations__in=self.object.specializations.all()
            )
        
        # Фильтруем по городу
        if self.object.city:
            related_doctors = related_doctors.filter(city=self.object.city)
        
        return related_doctors.exclude(pk=self.object.pk)[:4]
    
    def _get_doctor_services(self):
        """
        Get services provided by the doctor.
        
        Returns:
            QuerySet: Doctor's services
        """
        content_type = ContentType.objects.get_for_model(self.object)
        return FacilityService.objects.filter(
            content_type=content_type,
            object_id=self.object.pk,
            is_active=True
        ).select_related('service')

    def _get_doctor_reviews(self):
        """
        Get reviews for the doctor.
        
        Returns:
            QuerySet: Doctor's reviews
        """
        from reviews.models import Review
        content_type = ContentType.objects.get_for_model(self.object)
        return Review.objects.filter(
            content_type=content_type,
            object_id=self.object.pk,
            is_published=True
        ).order_by('-created_at')

def load_more_doctors(request):
    """
    AJAX loading of additional doctors.
    
    TODO: Refactor to use custom manager.
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: JSON response with cards HTML and has_more flag
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = 12
        
        doctors = PrivateDoctor.objects.filter(is_active=True).order_by('last_name', 'first_name')[offset:offset + limit + 1]
        has_more = len(doctors) > limit
        doctors = doctors[:limit]
        
        cards_html = ''
        for doctor in doctors:
            cards_html += render_to_string(
                'includes/cards/private_doctor_card.html',
                {'doctor': doctor},
                request=request
            )
        
        return JsonResponse({
            'cards': cards_html,
            'has_more': has_more
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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
    Общий список всех учреждений.
    
    TODO: Рефакторить для использования кастомных managers.
    """
    template_name = 'facilities/facility_list.html'
    context_object_name = 'facilities'
    paginate_by = 12

    def get_queryset(self):
        # Объединяем клиники и реабилитационные центры
        clinics = Clinic.objects.all()
        rehab_centers = RehabCenter.objects.all()
        return list(clinics) + list(rehab_centers)

class ClinicListView(SearchMixin, PaginationMixin, ListView):
    """
    Список клиник с поиском и пагинацией.
    
    Использует кастомный ClinicManager для оптимизации запросов.
    """
    model = Clinic
    template_name = 'facilities/clinic_list.html'
    context_object_name = 'clinics'
    paginate_by = 12
    
    # Настройки поиска
    search_fields = ['name', 'description', 'address']
    search_param = 'search'

    def get_queryset(self):
        """Используем кастомный manager для оптимизации."""
        queryset = Clinic.objects.with_related_data()
        
        # Применяем поиск из миксина
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # SEO контекст
        context['meta_title'] = 'Клиники лечения зависимостей - Центр помощи зависимым'
        context['meta_description'] = 'Найдите лучшие клиники для лечения алкоголизма, наркомании и игромании по всей России. Профессиональная помощь, анонимно, 24/7.'
        
        return context

class RehabilitationCenterListView(SearchMixin, PaginationMixin, ListView):
    """
    Список реабилитационных центров с поиском и пагинацией.
    
    Использует кастомный RehabCenterManager для оптимизации запросов.
    """
    model = RehabCenter
    template_name = 'facilities/rehabilitation_list.html'
    context_object_name = 'rehabilitation_centers'
    paginate_by = 12
    
    # Настройки поиска
    search_fields = ['name', 'description', 'address']
    search_param = 'search'

    def get_queryset(self):
        """Используем кастомный manager для оптимизации."""
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
        context = super().get_context_data(**kwargs)
        
        # SEO контекст
        context['meta_title'] = 'Реабилитационные центры - Центр помощи зависимым'
        context['meta_description'] = 'Реабилитационные центры для лечения зависимостей по всей России. Программы реабилитации, детоксикация, ресоциализация. Анонимно.'
        
        return context

class FacilityDetailView(GeoDataMixin, DetailView):
    """
    Детальное представление учреждения.
    
    Поддерживает разные типы учреждений (клиники, реабилитационные центры).
    """
    context_object_name = 'facility'

    def get_model(self):
        facility_type = self.kwargs.get('facility_type')
        if facility_type == 'clinic':
            return Clinic
        elif facility_type == 'rehab':
            return RehabCenter
        raise ValueError("Invalid facility type")

    def get_template_name(self):
        facility_type = self.kwargs.get('facility_type')
        if facility_type == 'clinic':
            return 'facilities/clinic_detail.html'
        elif facility_type == 'rehab':
            return 'facilities/rehabcenter_detail.html'
        raise ValueError("Invalid facility type")

    def get_queryset(self):
        """Используем кастомный manager для оптимизации."""
        model = self.get_model()
        if model == Clinic:
            return Clinic.objects.with_full_data()
        elif model == RehabCenter:
            return RehabCenter.objects.with_full_data()
        return model.objects.all()

    def get_context_data(self, **kwargs):
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
        
        # SEO
        context['meta_title'] = self.object.meta_title or self.object.name
        context['meta_description'] = self.object.meta_description or (self.object.description[:160] if self.object.description else '')
        context['meta_keywords'] = self.object.meta_keywords
        context['meta_image'] = self.object.meta_image.url if self.object.meta_image else None
        return context
    
    def _get_related_facilities(self, model):
        """Получение связанных учреждений."""
        related_facilities = model.objects.all()
        
        if self.object.city and self.object.city.region:
            related_facilities = related_facilities.filter(
                city__region=self.object.city.region
            ).exclude(pk=self.object.pk)
        
        return related_facilities[:4]
    
    def _get_facility_services(self):
        """Получение услуг учреждения."""
        content_type = ContentType.objects.get_for_model(self.object)
        return FacilityService.objects.filter(
            content_type=content_type,
            object_id=self.object.pk,
            is_active=True
        ).select_related('service').order_by('-service__display_priority', 'service__name')

def load_more_rehabs(request):
    """
    AJAX-загрузка дополнительных реабилитационных центров.
    
    TODO: Рефакторить для использования кастомного manager.
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
    AJAX-загрузка дополнительных клиник.
    
    TODO: Рефакторить для использования кастомного manager.
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
    Список частных врачей с поиском, фильтрацией и пагинацией.
    
    Использует кастомный PrivateDoctorManager для оптимизации запросов.
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
        """Используем кастомный manager для оптимизации."""
        queryset = PrivateDoctor.objects.with_related_data()
        
        # Применяем фильтры из миксинов
        return super().get_queryset()

    def get_context_data(self, **kwargs):
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
    Детальное представление частного врача.
    
    Использует кастомный manager для оптимизации запросов.
    """
    model = PrivateDoctor
    template_name = 'facilities/private_doctor_detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        """Используем кастомный manager для оптимизации."""
        return PrivateDoctor.objects.with_full_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем связанных врачей
        related_doctors = self._get_related_doctors()
        
        # Получаем услуги врача
        services = self._get_doctor_services()
        
        context['related_doctors'] = related_doctors
        context['services'] = services
        
        # SEO
        context['meta_title'] = self.object.meta_title or self.object.get_full_name()
        context['meta_description'] = self.object.meta_description or (self.object.biography[:160] if self.object.biography else '')
        context['meta_keywords'] = self.object.meta_keywords
        context['meta_image'] = self.object.meta_image.url if self.object.meta_image else None
        return context
    
    def _get_related_doctors(self):
        """Получение связанных врачей."""
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
        """Получение услуг врача."""
        content_type = ContentType.objects.get_for_model(self.object)
        return FacilityService.objects.filter(
            content_type=content_type,
            object_id=self.object.pk,
            is_active=True
        ).select_related('service')

def load_more_doctors(request):
    """
    AJAX-загрузка дополнительных врачей.
    
    TODO: Рефакторить для использования кастомного manager.
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

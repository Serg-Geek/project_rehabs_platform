from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Clinic, RehabCenter, PrivateDoctor
from medical_services.models import FacilityService, Service
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import models

# Create your views here.

class FacilityListView(ListView):
    template_name = 'facilities/facility_list.html'
    context_object_name = 'facilities'
    paginate_by = 12

    def get_queryset(self):
        # Объединяем клиники и реабилитационные центры
        clinics = Clinic.objects.all()
        rehab_centers = RehabCenter.objects.all()
        return list(clinics) + list(rehab_centers)

class ClinicListView(ListView):
    model = Clinic
    template_name = 'facilities/clinic_list.html'
    context_object_name = 'clinics'
    paginate_by = 12

    def get_queryset(self):
        queryset = Clinic.objects.all().prefetch_related(
            'images',
            'city',
            'city__region'
        ).order_by('id')
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_more'] = self.get_queryset().count() > self.paginate_by
        return context

class RehabilitationCenterListView(ListView):
    model = RehabCenter
    template_name = 'facilities/rehabilitation_list.html'
    context_object_name = 'rehabilitation_centers'
    paginate_by = 12

    def get_queryset(self):
        queryset = RehabCenter.objects.all().prefetch_related(
            'images',
            'city',
            'city__region'
        ).order_by('id')
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_more'] = self.get_queryset().count() > self.paginate_by
        return context

class FacilityDetailView(DetailView):
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
        return self.get_model().objects.prefetch_related(
            'reviews',
            'images',
            'documents',
            'specialists',
            'city',
            'city__region'
        ).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_model()
        related_facilities = model.objects.all()
        
        if self.object.city and self.object.city.region:
            related_facilities = related_facilities.filter(
                city__region=self.object.city.region
            ).exclude(pk=self.object.pk)
        
        related_facilities = related_facilities[:4]
        
        content_type = ContentType.objects.get_for_model(self.object)
        services = FacilityService.objects.filter(
            content_type=content_type,
            object_id=self.object.pk,
            is_active=True
        ).select_related('service')

        if isinstance(self.object, Clinic):
            context['clinic'] = self.object
        elif isinstance(self.object, RehabCenter):
            context['center'] = self.object
        
        context['related_facilities'] = related_facilities
        context['services'] = services
        context['facility_type'] = self.kwargs.get('facility_type')
        
        # --- Добавляем from_service_obj для хлебных крошек ---
        from_service_slug = self.request.GET.get('from_service')
        if from_service_slug:
            try:
                from_service_obj = Service.objects.get(slug=from_service_slug)
                context['from_service_obj'] = from_service_obj
            except Service.DoesNotExist:
                pass
        # ---
        return context

def load_more_rehabs(request):
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

class PrivateDoctorListView(ListView):
    model = PrivateDoctor
    template_name = 'facilities/private_doctors_list.html'
    context_object_name = 'doctors'
    paginate_by = 12

    def get_queryset(self):
        queryset = PrivateDoctor.objects.filter(is_active=True).prefetch_related(
            'specializations',
            'city',
            'city__region',
            'images'
        ).order_by('last_name', 'first_name')
        
        # Поиск по имени, специализации или городу
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(middle_name__icontains=search_query) |
                Q(specializations__name__icontains=search_query) |
                Q(city__name__icontains=search_query)
            ).distinct()
        
        # Фильтрация по городу
        city_filter = self.request.GET.get('city')
        if city_filter:
            queryset = queryset.filter(city__slug=city_filter)
        
        # Фильтрация по специализации
        specialization_filter = self.request.GET.get('specialization')
        if specialization_filter:
            queryset = queryset.filter(specializations__slug=specialization_filter)
        
        # Фильтрация по возможности выезда на дом
        home_visits = self.request.GET.get('home_visits')
        if home_visits == 'true':
            queryset = queryset.filter(home_visits=True)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['city_filter'] = self.request.GET.get('city', '')
        context['specialization_filter'] = self.request.GET.get('specialization', '')
        context['home_visits_filter'] = self.request.GET.get('home_visits', '')
        
        # Добавляем список всех специализаций для фильтра
        from staff.models import Specialization
        context['specializations'] = Specialization.objects.all().order_by('name')
        
        return context

class PrivateDoctorDetailView(DetailView):
    model = PrivateDoctor
    template_name = 'facilities/private_doctor_detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        return PrivateDoctor.objects.filter(is_active=True).prefetch_related(
            'specializations',
            'city',
            'city__region',
            'images',
            'documents',
            'reviews'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Похожие врачи в том же городе
        related_doctors = PrivateDoctor.objects.filter(
            is_active=True,
            city=self.object.city
        ).exclude(pk=self.object.pk).prefetch_related('specializations')[:4]
        
        # Врачи с похожими специализациями
        similar_specializations = self.object.specializations.all()
        similar_doctors = PrivateDoctor.objects.filter(
            is_active=True,
            specializations__in=similar_specializations
        ).exclude(pk=self.object.pk).distinct()[:4]
        
        context['related_doctors'] = related_doctors
        context['similar_doctors'] = similar_doctors
        context['reviews'] = self.object.reviews.all().order_by('-created_at')[:5]
        context['documents'] = self.object.documents.filter(is_active=True)
        context['images'] = self.object.images.all().order_by('order', 'created_at')
        
        # --- Добавляем from_service_obj для хлебных крошек ---
        from_service_slug = self.request.GET.get('from_service')
        if from_service_slug:
            try:
                from_service_obj = Service.objects.get(slug=from_service_slug)
                context['from_service_obj'] = from_service_obj
            except Service.DoesNotExist:
                pass
        # ---
        return context

def load_more_doctors(request):
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

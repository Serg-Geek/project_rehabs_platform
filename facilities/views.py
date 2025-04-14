from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Clinic, RehabCenter
from medical_services.models import FacilityService
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
        return RehabCenter.objects.all().order_by('id')

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
        return self.get_model().objects.prefetch_related('reviews').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_model()
        related_facilities = model.objects.all()
        
        if self.object.city and self.object.city.region:
            related_facilities = related_facilities.filter(
                city__region=self.object.city.region
            )
        
        related_facilities = related_facilities.exclude(pk=self.object.pk)[:4]
        
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

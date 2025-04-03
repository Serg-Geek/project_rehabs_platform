from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import MedicalFacility

# Create your views here.

class FacilityListView(ListView):
    model = MedicalFacility
    template_name = 'facilities/facility_list.html'
    context_object_name = 'facilities'
    paginate_by = 12

class ClinicListView(ListView):
    model = MedicalFacility
    template_name = 'facilities/clinic_list.html'
    context_object_name = 'clinics'
    paginate_by = 12

    def get_queryset(self):
        queryset = MedicalFacility.objects.filter(organization_type__slug='clinic')
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

class RehabilitationCenterListView(ListView):
    model = MedicalFacility
    template_name = 'facilities/rehabilitation_list.html'
    context_object_name = 'rehabilitation_centers'
    queryset = MedicalFacility.objects.filter(organization_type__slug='rehabilitation')
    paginate_by = 12

class SanatoriumListView(ListView):
    model = MedicalFacility
    template_name = 'facilities/sanatorium_list.html'
    context_object_name = 'sanatoriums'
    queryset = MedicalFacility.objects.filter(organization_type__slug='sanatorium')
    paginate_by = 12

class FacilityDetailView(DetailView):
    model = MedicalFacility
    template_name = 'facilities/facility_detail.html'
    context_object_name = 'facility'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем связанные учреждения того же типа в том же регионе
        context['related_facilities'] = MedicalFacility.objects.filter(
            organization_type=self.object.organization_type,
            city__region=self.object.city.region
        ).exclude(
            pk=self.object.pk
        )[:3]  # Ограничиваем до 3 связанных учреждений
        return context

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
    queryset = MedicalFacility.objects.filter(organization_type__slug='clinic')
    paginate_by = 12

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

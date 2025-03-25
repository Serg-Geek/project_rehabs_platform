from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from facilities.models.facility import MedicalInstitution, PrivateDoctor, BaseFacility
from django.http import Http404



class FacilityListView(ListView):
    template_name = "facilities/facility_list.html"
    context_object_name = "facilities"
    paginate_by = 12

    def get_queryset(self):
        facility_type = self.kwargs["facility_type"]
        
        if facility_type == 'rehab':
            return MedicalInstitution.objects.filter(type='rehab').select_related('city')
        elif facility_type == 'clinic':
            return MedicalInstitution.objects.filter(type='clinic').select_related('city')
        elif facility_type == 'doctors':
            return PrivateDoctor.objects.all().select_related('city')
        
        raise Http404("Invalid facility type")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['facility_type'] = self.kwargs["facility_type"]
        
        # Для правильного отображения заголовка страницы
        type_titles = {
            'rehab': 'Реабилитационные центры',
            'clinic': 'Клиники',
            'doctors': 'Частные врачи'
        }
        context['page_title'] = type_titles.get(self.kwargs["facility_type"], 'Каталог')
        
        return context


class MedicalInstitutionDetailView(DetailView):
    model = MedicalInstitution
    template_name = "facilities/medical_institution_detail.html"
    context_object_name = "facility"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.object.services.filter(is_available=True)
        context['specialists'] = self.object.specialists.all()
        return context


class PrivateDoctorDetailView(DetailView):
    model = PrivateDoctor
    template_name = "facilities/private_doctor_detail.html"
    context_object_name = "doctor"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.object.services.filter(is_available=True)
        context['primary_service'] = self.object.services.filter(is_primary=True).first()
        return context
    
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Clinic, RehabCenter

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
        queryset = Clinic.objects.all()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset

class RehabilitationCenterListView(ListView):
    model = RehabCenter
    template_name = 'facilities/rehabilitation_list.html'
    context_object_name = 'rehabilitation_centers'
    paginate_by = 12

    def get_queryset(self):
        return RehabCenter.objects.all()

class FacilityDetailView(DetailView):
    template_name = 'facilities/facility_detail.html'
    context_object_name = 'facility'

    def get_model(self):
        # Определяем модель на основе типа учреждения
        facility_type = self.kwargs.get('facility_type')
        if facility_type == 'clinic':
            return Clinic
        elif facility_type == 'rehab':
            return RehabCenter
        raise ValueError("Invalid facility type")

    def get_queryset(self):
        return self.get_model().objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем связанные учреждения того же типа в том же регионе
        model = self.get_model()
        context['related_facilities'] = model.objects.filter(
            city__region=self.object.city.region
        ).exclude(
            pk=self.object.pk
        )[:3]  # Ограничиваем до 3 связанных учреждений
        return context

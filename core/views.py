from django.shortcuts import render
from django.views.generic import TemplateView
from facilities.models import RehabCenter, Clinic
from staff.models import MedicalSpecialist

# Create your views here.

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем активные реабилитационные центры
        context['rehab_centers'] = RehabCenter.objects.filter(
            is_active=True
        ).select_related('city', 'city__region')[:6]
        
        # Получаем активные клиники
        context['clinics'] = Clinic.objects.filter(
            is_active=True
        ).select_related('city', 'city__region')[:6]
        
        # Получаем активных специалистов
        context['specialists'] = MedicalSpecialist.objects.filter(
            is_active=True
        )[:6]
        
        return context

class ContactsView(TemplateView):
    template_name = 'contacts.html'

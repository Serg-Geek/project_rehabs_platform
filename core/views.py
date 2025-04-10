from django.shortcuts import render
from django.views.generic import TemplateView
from facilities.models import RehabCenter, Clinic
from staff.models import MedicalSpecialist
from medical_services.models import ServiceCategory, Service

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

        # Получаем категории услуг для главной страницы
        service_categories = {
            'alcoholism': ServiceCategory.objects.get(slug='lechenie-alkogolizma'),
            'drug_addiction': ServiceCategory.objects.get(slug='lechenie-narkomanii'),
            'other': ServiceCategory.objects.get(slug='drugie-uslugi')
        }
        
        # Получаем услуги для каждой категории
        context['service_categories'] = {}
        for key, category in service_categories.items():
            context['service_categories'][key] = {
                'category': category,
                'services': Service.objects.filter(
                    categories=category,
                    is_active=True
                ).order_by('name')
            }
        
        return context

class ContactsView(TemplateView):
    template_name = 'contacts.html'

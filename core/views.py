from django.shortcuts import render
from django.views.generic import TemplateView
from facilities.models import RehabCenter, Clinic, PrivateDoctor
from staff.models import MedicalSpecialist
from medical_services.models import ServiceCategory, Service
from recovery_stories.models import RecoveryStory
from blog.models import Tag, BlogPost

# Create your views here.

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # SEO контекст
        context['meta_title'] = 'Центр помощи зависимым - Лечение алкоголизма, наркомании, игромании по всей России'
        context['meta_description'] = 'Профессиональная помощь в лечении зависимостей. Реабилитационные центры, клиники, частные врачи по всей России. Анонимно, 24/7. Бесплатная консультация.'
        
        # Получаем данные для главной страницы
        context['rehab_centers'] = RehabCenter.objects.filter(is_active=True).order_by('-created_at')[:12]
        context['clinics'] = Clinic.objects.filter(is_active=True).order_by('-created_at')[:12]
        context['private_doctors'] = PrivateDoctor.objects.filter(is_active=True).order_by('-created_at')[:12]
        context['specialists'] = MedicalSpecialist.objects.filter(is_active=True).order_by('-created_at')[:12]
        context['recovery_stories'] = RecoveryStory.objects.filter(is_published=True).order_by('-created_at')[:6]
        context['useful_info_cards'] = BlogPost.objects.filter(is_published=True).order_by('-created_at')[:3]
        
        # Получаем услуги для футера
        context['service_categories'] = self.get_service_categories()
        context['footer_services'] = self.get_footer_services()
        
        return context
    
    def get_service_categories(self):
        """Получает категории услуг для главной страницы"""
        return ServiceCategory.objects.filter(is_active=True).order_by('name')[:6]
    
    def get_footer_services(self):
        """Получает услуги для футера"""
        return Service.objects.filter(is_active=True).order_by('name')[:8]

class ContactsView(TemplateView):
    template_name = 'contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = 'Контакты - Центр помощи зависимым'
        context['meta_description'] = 'Свяжитесь с нами для получения профессиональной помощи в лечении зависимостей. Анонимная консультация 24/7.'
        return context

class ConsultationView(TemplateView):
    template_name = 'consultation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta_title'] = 'Бесплатная консультация - Центр помощи зависимым'
        context['meta_description'] = 'Получите бесплатную анонимную консультацию по лечению зависимостей. Профессиональные специалисты готовы помочь.'
        return context

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

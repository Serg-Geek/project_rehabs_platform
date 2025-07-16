from django.shortcuts import render
from django.views.generic import TemplateView
from facilities.models import RehabCenter, Clinic
from staff.models import MedicalSpecialist
from medical_services.models import ServiceCategory, Service
from recovery_stories.models import RecoveryStory
from blog.models import Tag, BlogPost

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

        # Получаем истории выздоровления
        context['recovery_stories'] = RecoveryStory.objects.filter(
            is_published=True
        ).order_by('-created_at')[:3]

        # Получаем категории услуг для главной страницы
        service_categories = {}
        categories_mapping = {
            'alcoholism': 'lechenie-alkogolizma',
            'drug_addiction': 'lechenie-narkomanii',
            'other': 'drugie-uslugi'
        }
        
        # Получаем только активные категории
        for key, slug in categories_mapping.items():
            try:
                category = ServiceCategory.objects.get(slug=slug, is_active=True)
                service_categories[key] = {
                    'category': category,
                    'services': Service.objects.filter(
                        categories=category,
                        is_active=True
                    ).order_by('name')
                }
            except ServiceCategory.DoesNotExist:
                continue
        
        context['service_categories'] = service_categories

        # Получаем карточки полезной информации из постов блога
        context['useful_info_cards'] = BlogPost.objects.filter(
            is_published=True,
            is_featured=True
        ).prefetch_related('tags').order_by('-publish_date')[:3]
        
        return context

class ContactsView(TemplateView):
    template_name = 'contacts.html'

class ConsultationView(TemplateView):
    template_name = 'consultation.html'

def page_not_found(request, exception):
    return render(request, '404.html', status=404)

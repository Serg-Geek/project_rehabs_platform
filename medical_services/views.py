from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from .models import ServiceCategory, Service, FacilityService
from facilities.models import Clinic, RehabCenter, PrivateDoctor


class ServiceCategoryListView(ListView):
    """Список всех категорий услуг"""
    model = ServiceCategory
    template_name = 'medical_services/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return ServiceCategory.objects.filter(
            is_active=True,
            parent__isnull=True  # Только родительские категории
        ).prefetch_related('children', 'services').order_by('order', 'name')


class ServiceCategoryDetailView(DetailView):
    """Детальная страница категории с услугами"""
    model = ServiceCategory
    template_name = 'medical_services/category_detail.html'
    context_object_name = 'category'
    
    def get_queryset(self):
        return ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем услуги категории
        services = Service.objects.filter(
            categories=self.object,
            is_active=True
        ).order_by('name')
        
        context['services'] = services
        return context


class ServiceDetailView(DetailView):
    """Детальная страница услуги с учреждениями"""
    model = Service
    template_name = 'medical_services/service_detail.html'
    context_object_name = 'service'
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True).prefetch_related('categories')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем учреждения, предоставляющие эту услугу
        facility_services = FacilityService.objects.filter(
            service=self.object,
            is_active=True
        ).select_related(
            'service'
        ).prefetch_related(
            'specialists'
        ).order_by('content_type__model')
        
        # Группируем по типам учреждений
        clinics = []
        rehab_centers = []
        private_doctors = []
        
        # Получаем ContentType для каждого типа учреждения
        try:
            clinic_ct = ContentType.objects.get(app_label='facilities', model='clinic')
            rehab_ct = ContentType.objects.get(app_label='facilities', model='rehabcenter')
            doctor_ct = ContentType.objects.get(app_label='facilities', model='privatedoctor')
            
            for fs in facility_services:
                if fs.content_type == clinic_ct:
                    # Получаем клинику
                    try:
                        clinic = Clinic.objects.get(id=fs.object_id)
                        clinics.append({
                            'facility_service': fs,
                            'facility': clinic
                        })
                    except Clinic.DoesNotExist:
                        continue
                elif fs.content_type == rehab_ct:
                    # Получаем реабилитационный центр
                    try:
                        rehab = RehabCenter.objects.get(id=fs.object_id)
                        rehab_centers.append({
                            'facility_service': fs,
                            'facility': rehab
                        })
                    except RehabCenter.DoesNotExist:
                        continue
                elif fs.content_type == doctor_ct:
                    # Получаем частного врача
                    try:
                        doctor = PrivateDoctor.objects.get(id=fs.object_id)
                        private_doctors.append({
                            'facility_service': fs,
                            'facility': doctor
                        })
                    except PrivateDoctor.DoesNotExist:
                        continue
        except ContentType.DoesNotExist:
            # Если ContentType не найдены, оставляем списки пустыми
            pass
        
        context.update({
            'clinics': clinics,
            'rehab_centers': rehab_centers,
            'private_doctors': private_doctors,
            'total_facilities': len(facility_services)
        })
        
        return context


class ServiceListView(ListView):
    """Список всех услуг"""
    model = Service
    template_name = 'medical_services/service_list.html'
    context_object_name = 'services'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).prefetch_related(
            'categories'
        ).order_by('name')
        
        # Фильтрация по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        
        # Поиск по названию
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True).order_by('name')
        return context

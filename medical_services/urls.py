from django.urls import path
from . import views

app_name = 'medical_services'

urlpatterns = [
    # Детальная страница категории
    path('category/<slug:slug>/', views.ServiceCategoryDetailView.as_view(), name='category_detail'),
    
    # Список всех услуг
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    
    # Детальная страница услуги с учреждениями
    path('service/<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
] 
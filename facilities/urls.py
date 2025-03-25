# facilities/urls.py
from django.urls import path
from facilities.views import (
    FacilityListView,
    MedicalInstitutionDetailView,
    PrivateDoctorDetailView
)

app_name = 'facilities'

urlpatterns = [
    # Список учреждений/врачей по типу
    path('<str:facility_type>/', FacilityListView.as_view(), name='facility_list'),
    
    # Детальная страница медицинского учреждения
    path('institutions/<slug:slug>/', 
        MedicalInstitutionDetailView.as_view(), 
        name='institution_detail'),
    
    # Детальная страница частного врача
    path('doctors/<slug:slug>/', 
        PrivateDoctorDetailView.as_view(), 
        name='doctor_detail'),
]
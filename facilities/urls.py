from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('', views.FacilityListView.as_view(), name='list'),
    path('clinics/', views.ClinicListView.as_view(), name='clinic_list'),
    path('rehabilitation/', views.RehabilitationCenterListView.as_view(), name='rehabilitation_list'),
    path('rehabs/', views.RehabilitationCenterListView.as_view(), name='rehab_list'),
    path('clinic/<slug:slug>/', views.FacilityDetailView.as_view(), kwargs={'facility_type': 'clinic'}, name='clinic_detail'),
    path('rehabilitation/<slug:slug>/', views.FacilityDetailView.as_view(), kwargs={'facility_type': 'rehab'}, name='rehab_detail'),
    path('load-more-rehabs/', views.load_more_rehabs, name='load_more_rehabs'),
    path('load-more-clinics/', views.load_more_clinics, name='load_more_clinics'),
] 
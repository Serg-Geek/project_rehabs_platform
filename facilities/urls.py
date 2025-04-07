from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('', views.FacilityListView.as_view(), name='list'),
    path('clinic/', views.ClinicListView.as_view(), name='clinic_list'),
    path('rehabilitation/', views.RehabilitationCenterListView.as_view(), name='rehabilitation_list'),
    path('clinic/<slug:slug>/', views.FacilityDetailView.as_view(), kwargs={'facility_type': 'clinic'}, name='clinic_detail'),
    path('rehabilitation/<slug:slug>/', views.FacilityDetailView.as_view(), kwargs={'facility_type': 'rehab'}, name='rehab_detail'),
] 
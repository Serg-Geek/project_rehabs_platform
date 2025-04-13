from django.urls import path
from . import views

app_name = 'requests'

urlpatterns = [
    path('consultation/', views.ConsultationRequestView.as_view(), name='consultation_request'),
    path('partner/', views.PartnerRequestView.as_view(), name='partner_request'),
    path('success/', views.success_view, name='success'),
    path('error/', views.error_view, name='error'),
] 
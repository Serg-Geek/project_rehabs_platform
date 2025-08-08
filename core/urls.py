from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
] 
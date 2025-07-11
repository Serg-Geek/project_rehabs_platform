from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.SpecialistsListView.as_view(), name='specialists_list'),
    path('<slug:slug>/', views.SpecialistDetailView.as_view(), name='specialist_detail'),
] 
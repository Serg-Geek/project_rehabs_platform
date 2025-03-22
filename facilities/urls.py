from django.urls import path
from facilities import views

app_name = 'facilities'

urlpatterns = [
    path("clinics/", views.clinics_catalog, name="clinics_catalog"),  
    path("clinic_detail/", views.clinic_detail, name="clinic_detail"),
    # path("rehabs/", views.rehabs_list, name="rehabs_list"),  # Каталог рехабов
    # path("<int:pk>/", views.facility_detail, name="facility_detail"),  # Детальная страница
]

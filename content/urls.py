from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('banner/', views.BannerView.as_view(), name='banner'),
] 
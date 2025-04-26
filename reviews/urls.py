from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path(
        'specialist/<int:specialist_id>/',
        views.ReviewListView.as_view(),
        name='list'
    ),
    path(
        'specialist/<int:specialist_id>/create/',
        views.ReviewCreateView.as_view(),
        name='create'
    ),
    path(
        '<int:pk>/update/',
        views.ReviewUpdateView.as_view(),
        name='update'
    ),
    path(
        '<int:pk>/delete/',
        views.ReviewDeleteView.as_view(),
        name='delete'
    ),
    path(
        'facility/<str:facility_type>/<int:facility_id>/create/',
        views.FacilityReviewCreateView.as_view(),
        name='facility_create'
    ),
] 
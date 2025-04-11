from django.urls import path
from .views import StoryListView, StoryDetailView

app_name = 'recovery_stories'

urlpatterns = [
    path('stories/', StoryListView.as_view(), name='list'),
    path('stories/category/<slug:slug>/', StoryListView.as_view(), name='category_stories'),
    path('stories/<slug:slug>/', StoryDetailView.as_view(), name='detail'),
] 
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogPostListView.as_view(), name='post_list'),
    path('category/<slug:slug>/', views.BlogPostListByCategoryView.as_view(), name='post_list_by_category'),
    path('post/<slug:slug>/', views.BlogPostDetailView.as_view(), name='post_detail'),
] 
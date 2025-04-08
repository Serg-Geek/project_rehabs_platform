from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import BlogPost, BlogCategory, Tag

# Create your views here.

class PostListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True).select_related('category')
        
        # Фильтрация по категории
        category_slug = self.kwargs.get('slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Фильтрация по тегу
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug, is_active=True)
            queryset = queryset.filter(tags=tag)
        
        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(preview_text__icontains=search_query)
            )
        
        return queryset.order_by('-publish_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(parent=None)
        context['active_tag'] = self.request.GET.get('tag')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Добавляем текущую категорию, если есть
        category_slug = self.kwargs.get('slug')
        if category_slug:
            context['current_category'] = get_object_or_404(BlogCategory, slug=category_slug)
        
        return context

class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('images', 'post_tags__tag')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(parent=None)
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

class BlogPostListByCategoryView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get('slug')
        return BlogPost.objects.filter(
            is_published=True,
            category__slug=category_slug
        ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        context['current_category'] = BlogCategory.objects.get(slug=self.kwargs.get('slug'))
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).select_related('category').prefetch_related('images', 'post_tags__tag')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        return context

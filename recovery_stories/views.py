from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import RecoveryStory, RecoveryCategory, RecoveryTag

# Create your views here.

class StoryListView(ListView):
    model = RecoveryStory
    template_name = 'recovery_stories/list.html'
    context_object_name = 'stories'
    paginate_by = 9

    def get_queryset(self):
        queryset = RecoveryStory.objects.filter(is_published=True).select_related('category', 'content_type')
        
        # Фильтрация по категории
        category_slug = self.kwargs.get('slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Фильтрация по тегу
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            tag = get_object_or_404(RecoveryTag, slug=tag_slug, is_active=True)
            queryset = queryset.filter(tags=tag)
        
        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        return queryset.order_by('-publish_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = RecoveryCategory.objects.filter(parent=None)
        context['active_tag'] = self.request.GET.get('tag')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Добавляем системные теги
        context['system_tags'] = RecoveryTag.objects.filter(is_system=True, is_active=True)
        
        # Добавляем текущую категорию, если есть
        category_slug = self.kwargs.get('slug')
        if category_slug:
            context['current_category'] = get_object_or_404(RecoveryCategory, slug=category_slug)
        
        return context

class StoryDetailView(DetailView):
    model = RecoveryStory
    template_name = 'recovery_stories/detail.html'
    context_object_name = 'story'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return RecoveryStory.objects.filter(is_published=True).select_related('category', 'content_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        # SEO
        context['meta_title'] = story.meta_title or story.title
        context['meta_description'] = story.meta_description or (story.excerpt[:160] if story.excerpt else '')
        
        # Увеличиваем счетчик просмотров
        story.views += 1
        story.save(update_fields=['views'])
        
        # Добавляем системные теги
        context['system_tags'] = RecoveryTag.objects.filter(is_system=True, is_active=True)
        
        # Добавляем похожие истории
        context['related_stories'] = RecoveryStory.objects.filter(
            is_published=True,
            category=story.category
        ).exclude(id=story.id).order_by('-publish_date')[:3]
        
        return context

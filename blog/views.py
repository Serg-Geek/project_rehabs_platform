from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import BlogPost, BlogCategory, Tag
from core.mixins import SearchMixin, FilterMixin, PaginationMixin, CacheMixin

# Create your views here.

class PostListView(SearchMixin, FilterMixin, PaginationMixin, ListView):
    """
    Представление для списка постов блога с поиском, фильтрацией и пагинацией.
    
    Использует миксины для переиспользуемой функциональности.
    """
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    # Настройки поиска
    search_fields = ['title', 'content', 'preview_text']
    search_param = 'search'
    
    # Настройки фильтрации
    filter_fields = {
        'category': 'category__slug',
        'tag': 'tags__slug'
    }
    
    def get_queryset(self):
        """Получение базового queryset с оптимизацией."""
        queryset = BlogPost.objects.filter(is_published=True)\
                                   .select_related('category')\
                                   .prefetch_related('tags', 'images')
        
        # Применяем фильтры из миксинов
        queryset = super().get_queryset()
        
        # Фильтрация по категории из URL
        category_slug = self.kwargs.get('slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Фильтрация по тегу из GET параметра
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug, is_active=True)
            queryset = queryset.filter(tags=tag)
        
        return queryset.order_by('-publish_date')

    def get_context_data(self, **kwargs):
        """Добавление дополнительных данных в контекст."""
        context = super().get_context_data(**kwargs)
        
        # Добавляем категории
        context['categories'] = BlogCategory.objects.filter(parent=None)
        
        # Добавляем системные теги
        context['system_tags'] = Tag.objects.filter(is_system=True, is_active=True)
        
        # Добавляем активный тег
        context['active_tag'] = self.request.GET.get('tag')
        
        # Добавляем текущую категорию, если есть
        category_slug = self.kwargs.get('slug')
        if category_slug:
            context['current_category'] = get_object_or_404(
                BlogCategory, slug=category_slug
            )
        
        return context


class PostDetailView(DetailView):
    """
    Представление для детального просмотра поста.
    
    Оптимизировано для производительности с prefetch_related.
    """
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Оптимизированный queryset с prefetch_related."""
        return BlogPost.objects.filter(is_published=True)\
                               .select_related('category')\
                               .prefetch_related('images', 'post_tags__tag')

    def get_context_data(self, **kwargs):
        """Добавление дополнительных данных в контекст."""
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(parent=None)
        
        # Добавляем связанные посты
        post = self.get_object()
        context['related_posts'] = self._get_related_posts(post)
        
        # SEO
        context['meta_title'] = post.meta_title or post.title
        context['meta_description'] = post.meta_description or (post.preview_text[:160] if post.preview_text else '')
        
        return context

    def get_object(self, queryset=None):
        """Увеличение счетчика просмотров при получении объекта."""
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def _get_related_posts(self, post, limit=3):
        """Получение связанных постов."""
        try:
            return BlogPost.objects.filter(
                is_published=True,
                category=post.category
            ).exclude(id=post.id)\
             .select_related('category')\
             .order_by('-publish_date')[:limit]
        except Exception:
            return []


class BlogPostListByCategoryView(SearchMixin, PaginationMixin, ListView):
    """
    Представление для списка постов по категории.
    
    Использует миксины для поиска и пагинации.
    """
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    # Настройки поиска
    search_fields = ['title', 'content', 'preview_text']
    search_param = 'search'

    def get_queryset(self):
        """Получение постов по категории с оптимизацией."""
        category_slug = self.kwargs.get('slug')
        queryset = BlogPost.objects.filter(
            is_published=True,
            category__slug=category_slug
        ).select_related('category')\
         .prefetch_related('tags', 'images')
        
        # Применяем поиск из миксина
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        """Добавление данных категории в контекст."""
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        context['current_category'] = BlogCategory.objects.get(
            slug=self.kwargs.get('slug')
        )
        return context


class BlogPostDetailView(DetailView):
    """
    Дублирующее представление для детального просмотра поста.
    
    TODO: Удалить после рефакторинга URL-ов.
    """
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """Оптимизированный queryset."""
        return BlogPost.objects.filter(is_published=True)\
                               .select_related('category')\
                               .prefetch_related('images', 'post_tags__tag')

    def get_context_data(self, **kwargs):
        """Добавление категорий в контекст."""
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        # SEO
        context['meta_title'] = post.meta_title or post.title
        context['meta_description'] = post.meta_description or (post.preview_text[:160] if post.preview_text else '')
        context['categories'] = BlogCategory.objects.all()
        return context

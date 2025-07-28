from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import BlogPost, BlogCategory, Tag
from core.mixins import SearchMixin, FilterMixin, PaginationMixin, CacheMixin

# Create your views here.

class PostListView(SearchMixin, FilterMixin, PaginationMixin, ListView):
    """
    View for blog post list with search, filtering and pagination.
    
    Uses mixins for reusable functionality.
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
        """
        Get optimized queryset with related data.
        
        Returns:
            QuerySet: Optimized queryset with category and tag filtering
        """
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
        """
        Add additional data to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with categories, tags and current category
        """
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
    View for detailed blog post display.
    
    Optimized for performance with prefetch_related.
    """
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """
        Get optimized queryset with prefetch_related.
        
        Returns:
            QuerySet: Optimized queryset with related data
        """
        return BlogPost.objects.filter(is_published=True)\
                               .select_related('category')\
                               .prefetch_related('images', 'post_tags__tag')

    def get_context_data(self, **kwargs):
        """
        Add additional data to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with categories, related posts and SEO data
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(parent=None)
        
        # Добавляем связанные посты
        post = self.get_object()
        context['related_posts'] = self._get_related_posts(post)
        
        # SEO
        context['meta_title'] = post.meta_title or post.title
        context['meta_description'] = post.meta_description or (post.preview_text[:160] if post.preview_text else '')
        context['meta_keywords'] = post.meta_keywords
        context['meta_image'] = post.meta_image.url if post.meta_image else None
        
        return context

    def get_object(self, queryset=None):
        """
        Get the post object and increment view count.
        
        Args:
            queryset: Optional queryset to use
            
        Returns:
            BlogPost: Post object with incremented view count
        """
        obj = super().get_object(queryset)
        # Увеличиваем счетчик просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj
    
    def _get_related_posts(self, post, limit=3):
        """
        Get related posts based on category.
        
        Args:
            post: Current post instance
            limit: Maximum number of related posts
            
        Returns:
            QuerySet: Related posts or empty list on error
        """
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
    View for blog post list by category.
    
    Uses mixins for search and pagination.
    """
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    # Настройки поиска
    search_fields = ['title', 'content', 'preview_text']
    search_param = 'search'

    def get_queryset(self):
        """
        Get posts by category with optimization.
        
        Returns:
            QuerySet: Optimized queryset filtered by category
        """
        category_slug = self.kwargs.get('slug')
        queryset = BlogPost.objects.filter(
            is_published=True,
            category__slug=category_slug
        ).select_related('category')\
         .prefetch_related('tags', 'images')
        
        # Применяем поиск из миксина
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        """
        Add category data to context.
        
        Args:
            **kwargs: Additional context data
            
        Returns:
            dict: Context with categories and current category
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        context['current_category'] = BlogCategory.objects.get(
            slug=self.kwargs.get('slug')
        )
        return context


class BlogPostDetailView(DetailView):
    """
    Duplicate view for detailed blog post display.
    
    TODO: Remove after URL refactoring.
    """
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

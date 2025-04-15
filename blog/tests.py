from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import BlogCategory, BlogPost, Tag, BlogPostTag
from django.utils.text import slugify

# Create your tests here.

class BlogCategoryTests(TestCase):
    def setUp(self):
        self.parent_data = {
            'name': 'Родительская категория',
            'description': 'Описание родительской категории'
        }
        self.child_data = {
            'name': 'Дочерняя категория',
            'description': 'Описание дочерней категории'
        }

    def test_create_category(self):
        """Тест создания категории"""
        category = BlogCategory.objects.create(**self.parent_data)
        self.assertEqual(category.name, self.parent_data['name'])
        self.assertEqual(category.slug, slugify(self.parent_data['name']))
        self.assertEqual(category.description, self.parent_data['description'])

    def test_category_hierarchy(self):
        """Тест иерархии категорий"""
        parent = BlogCategory.objects.create(**self.parent_data)
        child_data = self.child_data.copy()
        child_data['parent'] = parent
        child = BlogCategory.objects.create(**child_data)
        
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())
        self.assertTrue(child.slug.startswith(slugify(child_data['name'])))

class BlogPostTests(TestCase):
    def setUp(self):
        self.category = BlogCategory.objects.create(
            name='Тестовая категория',
            description='Описание тестовой категории'
        )
        self.post_data = {
            'title': 'Тестовый пост',
            'category': self.category,
            'preview_text': 'Краткое описание поста',
            'content': 'Полное содержание поста',
            'is_published': True
        }

    def test_create_post(self):
        """Тест создания поста"""
        post = BlogPost.objects.create(**self.post_data)
        self.assertEqual(post.title, self.post_data['title'])
        self.assertEqual(post.slug, slugify(self.post_data['title']))
        self.assertEqual(post.category, self.category)
        self.assertTrue(post.is_published)

    def test_post_required_fields(self):
        """Тест обязательных полей поста"""
        # Удаляем обязательное поле title
        post_data = self.post_data.copy()
        del post_data['title']
        
        post = BlogPost(**post_data)
        with self.assertRaises(ValidationError):
            post.full_clean()

class TagTests(TestCase):
    def setUp(self):
        self.tag_data = {
            'name': 'Тестовый тег',
            'description': 'Описание тестового тега'
        }

    def test_create_tag(self):
        """Тест создания тега"""
        tag = Tag.objects.create(**self.tag_data)
        self.assertEqual(tag.name, self.tag_data['name'])
        self.assertEqual(tag.slug, slugify(self.tag_data['name']))
        self.assertTrue(tag.is_active)

class BlogPostTagTests(TestCase):
    def setUp(self):
        self.category = BlogCategory.objects.create(
            name='Тестовая категория',
            description='Описание тестовой категории'
        )
        self.post = BlogPost.objects.create(
            title='Тестовый пост',
            category=self.category,
            preview_text='Краткое описание поста',
            content='Полное содержание поста',
            is_published=True
        )
        self.tag = Tag.objects.create(
            name='Тестовый тег',
            description='Описание тестового тега'
        )

    def test_create_post_tag_relation(self):
        """Тест создания связи между постом и тегом"""
        post_tag = BlogPostTag.objects.create(post=self.post, tag=self.tag)
        self.assertEqual(post_tag.post, self.post)
        self.assertEqual(post_tag.tag, self.tag)
        self.assertIn(self.tag, self.post.tags.all())
        self.assertIn(self.post, self.tag.blogpost_set.all())

    def test_unique_post_tag_relation(self):
        """Тест уникальности связи между постом и тегом"""
        # Создаем первую связь
        BlogPostTag.objects.create(post=self.post, tag=self.tag)
        
        # Пытаемся создать дублирующую связь
        duplicate = BlogPostTag(post=self.post, tag=self.tag)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

class BlogViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = BlogCategory.objects.create(
            name='Тестовая категория',
            description='Описание тестовой категории',
            slug='testovaya-kategoriya'
        )
        self.post = BlogPost.objects.create(
            title='Test Post',  # Используем английское название
            category=self.category,
            preview_text='Test preview text',  # Используем английский текст
            content='Test content',  # Используем английский текст
            is_published=True,
            slug='test-post'
        )
        self.tag = Tag.objects.create(
            name='Тестовый тег',
            description='Описание тестового тега',
            slug='testovyy-teg'
        )
        BlogPostTag.objects.create(post=self.post, tag=self.tag)

    def test_post_list_view(self):
        """Тест списка постов"""
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertIn('posts', response.context)
        self.assertIn(self.post, response.context['posts'])

    def test_post_detail_view(self):
        """Тест детальной страницы поста"""
        response = self.client.get(reverse('blog:post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertEqual(response.context['post'], self.post)

    def test_post_list_by_category(self):
        """Тест списка постов по категории"""
        response = self.client.get(reverse('blog:category_posts', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertIn('posts', response.context)
        self.assertIn(self.post, response.context['posts'])
        self.assertEqual(response.context['current_category'], self.category)

    def test_post_list_by_tag(self):
        """Тест списка постов по тегу"""
        response = self.client.get(reverse('blog:post_list') + f'?tag={self.tag.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertIn('posts', response.context)
        self.assertIn(self.post, response.context['posts'])
        self.assertEqual(response.context['active_tag'], self.tag.slug)

    def test_post_search(self):
        """Тест поиска постов"""
        response = self.client.get(reverse('blog:post_list') + '?search=test')  # Ищем по английскому слову
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertIn('posts', response.context)
        self.assertIn(self.post, response.context['posts'])
        self.assertEqual(response.context['search_query'], 'test')

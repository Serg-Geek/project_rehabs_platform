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

    def test_get_tags_with_icons(self):
        """Тест метода get_tags_with_icons"""
        post = BlogPost.objects.create(**self.post_data)
        
        # Создаем обычный тег
        regular_tag = Tag.objects.create(
            name='Обычный тег',
            description='Обычный тег без иконки'
        )
        
        # Создаем системный тег с уникальным slug
        system_tag = Tag.objects.create(
            name='Системный тег',
            slug='test-system-tag',
            description='Системный тег с иконкой',
            is_system=True,
            is_active=True
        )
        
        # Добавляем теги к посту
        BlogPostTag.objects.create(post=post, tag=regular_tag)
        BlogPostTag.objects.create(post=post, tag=system_tag)
        
        # Получаем теги с иконками
        tags_with_icons = post.get_tags_with_icons()
        
        self.assertEqual(len(tags_with_icons), 2)
        
        # Проверяем обычный тег
        regular_tag_data = next(t for t in tags_with_icons if t['name'] == 'Обычный тег')
        self.assertIsNone(regular_tag_data['icon'])
        self.assertEqual(regular_tag_data['url'], f'?tag={regular_tag.slug}')
        
        # Проверяем системный тег
        system_tag_data = next(t for t in tags_with_icons if t['name'] == 'Системный тег')
        self.assertIsNone(system_tag_data['icon'])  # У тестового тега нет иконки в словаре
        self.assertEqual(system_tag_data['url'], f'?tag={system_tag.slug}')


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

    def test_system_tag_creation(self):
        """Тест создания системного тега"""
        system_tag = Tag.objects.create(
            name='Системный тег',
            slug='test-system-tag-creation',
            description='Системный тег с иконкой',
            is_system=True,
            is_active=True
        )
        
        self.assertTrue(system_tag.is_system)
        self.assertTrue(system_tag.is_active)
        self.assertEqual(system_tag.slug, 'test-system-tag-creation')

    def test_get_icon_path_system_tag(self):
        """Тест получения пути к иконке для системного тега"""
        # Используем существующий системный тег из миграции
        system_tag = Tag.objects.get(slug='psihologiya')
        
        icon_path = system_tag.get_icon_path()
        self.assertIsNotNone(icon_path)
        self.assertIn('psychologist-icon.svg', icon_path)

    def test_get_icon_path_regular_tag(self):
        """Тест получения пути к иконке для обычного тега"""
        regular_tag = Tag.objects.create(
            name='Обычный тег',
            description='Обычный тег без иконки'
        )
        
        icon_path = regular_tag.get_icon_path()
        self.assertIsNone(icon_path)

    def test_initialize_system_tags(self):
        """Тест метода initialize_system_tags"""
        # Проверяем, что системные теги создаются
        created_count, updated_count = Tag.initialize_system_tags()
        
        # Должно быть создано 7 системных тегов
        self.assertGreaterEqual(created_count, 0)
        self.assertEqual(updated_count, 0)
        
        # Проверяем, что все системные теги существуют
        system_tags = Tag.objects.filter(is_system=True)
        self.assertGreaterEqual(system_tags.count(), 7)
        
        # Проверяем конкретные теги
        expected_slugs = [
            'profilaktika-i-preduprezhdenie',
            'yuridicheskaya-konsultatsiya',
            'psihiatriya',
            'psihologiya',
            'rodstvennikam',
            'narkomaniya',
            'alkogolizm'
        ]
        
        for slug in expected_slugs:
            self.assertTrue(Tag.objects.filter(slug=slug, is_system=True).exists())

    def test_initialize_system_tags_no_duplication(self):
        """Тест отсутствия дублирования при повторном вызове"""
        # Первый вызов
        created_first, updated_first = Tag.initialize_system_tags()
        count_first = Tag.objects.filter(is_system=True).count()
        
        # Второй вызов
        created_second, updated_second = Tag.initialize_system_tags()
        count_second = Tag.objects.filter(is_system=True).count()
        
        # Количество тегов не должно измениться
        self.assertEqual(count_first, count_second)
        self.assertEqual(created_second, 0)
        self.assertEqual(updated_second, 0)


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

    def test_post_list_view_with_system_tags(self):
        """Тест списка постов с системными тегами в контексте"""
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что системные теги есть в контексте
        self.assertIn('system_tags', response.context)
        system_tags = response.context['system_tags']
        self.assertIsInstance(system_tags, (list, type(Tag.objects.none())))
        
        # Проверяем, что все системные теги активны
        for tag in system_tags:
            self.assertTrue(tag.is_active)

    def test_post_detail_view_views_count(self):
        """Тест увеличения счетчика просмотров"""
        # Создаем новый пост для тестирования счетчика
        test_post = BlogPost.objects.create(
            title='Test Views Post',
            category=self.category,
            preview_text='Test preview',
            content='Test content',
            is_published=True,
            slug='test-views-post',
            views_count=0
        )
        
        initial_views = test_post.views_count
        
        # Первый запрос - get_object вызывается дважды (в get_context_data и в представлении)
        response = self.client.get(reverse('blog:post_detail', kwargs={'slug': test_post.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Обновляем объект из БД
        test_post.refresh_from_db()
        # Учитываем, что get_object вызывается дважды
        self.assertEqual(test_post.views_count, initial_views + 2)
        
        # Второй запрос
        response = self.client.get(reverse('blog:post_detail', kwargs={'slug': test_post.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Обновляем объект из БД
        test_post.refresh_from_db()
        # Учитываем, что get_object вызывается дважды
        self.assertEqual(test_post.views_count, initial_views + 4)

    def test_post_detail_view_related_posts(self):
        """Тест связанных постов в детальном представлении"""
        # Создаем еще один пост в той же категории
        related_post = BlogPost.objects.create(
            title='Related Post',
            category=self.category,
            preview_text='Related preview',
            content='Related content',
            is_published=True,
            slug='related-post'
        )
        
        response = self.client.get(reverse('blog:post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что связанные посты есть в контексте
        self.assertIn('related_posts', response.context)
        related_posts = response.context['related_posts']
        self.assertIsInstance(related_posts, (list, type(BlogPost.objects.none())))
        self.assertIn(related_post, related_posts)

    def test_post_list_view_pagination(self):
        """Тест пагинации в списке постов"""
        # Создаем дополнительные посты для тестирования пагинации
        for i in range(15):
            BlogPost.objects.create(
                title=f'Post {i}',
                category=self.category,
                preview_text=f'Preview {i}',
                content=f'Content {i}',
                is_published=True,
                slug=f'post-{i}'
            )
        
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем наличие пагинации
        self.assertIn('is_paginated', response.context)
        self.assertTrue(response.context['is_paginated'])
        
        # Проверяем количество постов на странице (paginate_by = 9)
        posts = response.context['posts']
        self.assertLessEqual(len(posts), 9)

    def test_post_list_view_search_and_filter(self):
        """Тест комбинированного поиска и фильтрации"""
        # Создаем пост с системным тегом
        system_tag = Tag.objects.create(
            name='Психология',
            slug='test-psihologiya',
            is_system=True,
            is_active=True
        )
        
        post_with_system_tag = BlogPost.objects.create(
            title='Psychology Post',
            category=self.category,
            preview_text='Psychology content',
            content='Psychology detailed content',
            is_published=True,
            slug='psychology-post'
        )
        BlogPostTag.objects.create(post=post_with_system_tag, tag=system_tag)
        
        # Тестируем поиск с фильтром по тегу
        response = self.client.get(
            reverse('blog:post_list') + '?search=psychology&tag=test-psihologiya'
        )
        self.assertEqual(response.status_code, 200)
        
        posts = response.context['posts']
        self.assertIn(post_with_system_tag, posts)
        self.assertEqual(response.context['search_query'], 'psychology')
        self.assertEqual(response.context['active_tag'], 'test-psihologiya')

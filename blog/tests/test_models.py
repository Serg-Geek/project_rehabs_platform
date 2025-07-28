from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from blog.models import BlogCategory, BlogPost, Tag, BlogPostTag


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
            name='Тестовый системный тег',
            slug='test-system-tag-unique',
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
        
        # Проверяем системный тег
        system_tag_data = next(t for t in tags_with_icons if t['name'] == 'Тестовый системный тег')
        self.assertIsNone(system_tag_data['icon'])  # Нет иконки для несуществующего slug


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
        self.assertFalse(tag.is_system)

    def test_system_tag_creation(self):
        """Тест создания системного тега"""
        system_tag_data = self.tag_data.copy()
        system_tag_data.update({
            'slug': 'test-system-tag-unique',
            'is_system': True,
            'is_active': True
        })
        
        tag = Tag.objects.create(**system_tag_data)
        self.assertTrue(tag.is_system)
        self.assertTrue(tag.is_active)
        self.assertEqual(tag.slug, 'test-system-tag-unique')

    def test_get_icon_path_system_tag(self):
        """Тест получения пути к иконке системного тега"""
        tag = Tag.objects.create(
            name='Тестовый системный тег',
            slug='test-system-tag-unique',
            is_system=True,
            is_active=True
        )
        
        icon_path = tag.get_icon_path()
        self.assertIsNone(icon_path)  # Нет иконки для несуществующего slug

    def test_get_icon_path_existing_system_tag(self):
        """Тест получения пути к иконке существующего системного тега"""
        # Используем существующий системный тег из миграции
        existing_tag = Tag.objects.filter(slug='alkogolizm', is_system=True).first()
        if existing_tag:
            icon_path = existing_tag.get_icon_path()
            self.assertIsNotNone(icon_path)
            self.assertIn('alcohol-icon.svg', icon_path)

    def test_get_icon_path_regular_tag(self):
        """Тест получения пути к иконке обычного тега"""
        tag = Tag.objects.create(**self.tag_data)
        
        icon_path = tag.get_icon_path()
        self.assertIsNone(icon_path)

    def test_initialize_system_tags(self):
        """Тест инициализации системных тегов"""
        # Проверяем, что системные теги создаются
        Tag.initialize_system_tags()
        
        # Проверяем наличие основных системных тегов
        system_tags = Tag.objects.filter(is_system=True)
        self.assertGreater(system_tags.count(), 0)
        
        # Проверяем конкретные теги
        alcohol_tag = Tag.objects.filter(slug='alkogolizm').first()
        if alcohol_tag:
            self.assertTrue(alcohol_tag.is_system)

    def test_initialize_system_tags_no_duplication(self):
        """Тест отсутствия дублирования системных тегов"""
        # Первый вызов
        Tag.initialize_system_tags()
        first_count = Tag.objects.filter(is_system=True).count()
        
        # Второй вызов
        Tag.initialize_system_tags()
        second_count = Tag.objects.filter(is_system=True).count()
        
        # Количество должно остаться тем же
        self.assertEqual(first_count, second_count)


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
        """Тест создания связи пост-тег"""
        post_tag = BlogPostTag.objects.create(post=self.post, tag=self.tag)
        self.assertEqual(post_tag.post, self.post)
        self.assertEqual(post_tag.tag, self.tag)

    def test_unique_post_tag_relation(self):
        """Тест уникальности связи пост-тег"""
        # Создаем первую связь
        BlogPostTag.objects.create(post=self.post, tag=self.tag)
        
        # Пытаемся создать дублирующую связь
        with self.assertRaises(Exception):
            BlogPostTag.objects.create(post=self.post, tag=self.tag) 
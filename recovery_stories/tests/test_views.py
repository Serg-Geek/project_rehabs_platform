from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from recovery_stories.models import RecoveryStory, RecoveryCategory, RecoveryTag

User = get_user_model()

class RecoveryStoriesViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Создаем категорию
        self.category = RecoveryCategory.objects.create(
            name='Алкоголизм',
            slug='alcoholism',
            description='Истории выздоровления от алкоголизма'
        )
        
        # Создаем тег
        self.tag = RecoveryTag.objects.create(
            name='Успешное выздоровление',
            slug='successful-recovery',
            description='Истории успешного выздоровления'
        )
        
        # Создаем опубликованную историю
        self.published_story = RecoveryStory.objects.create(
            title='Мой путь к выздоровлению',
            slug='my-recovery-path',
            category=self.category,
            author='Аноним',
            content='Полная история моего выздоровления...',
            excerpt='Краткое описание истории выздоровления',
            is_published=True,
            publish_date=timezone.now()
        )
        self.published_story.tags.add(self.tag)
        
        # Создаем неопубликованную историю
        self.unpublished_story = RecoveryStory.objects.create(
            title='Неопубликованная история',
            slug='unpublished-story',
            category=self.category,
            author='Аноним',
            content='Неопубликованная история...',
            excerpt='Краткое описание',
            is_published=False
        )

    def test_stories_list_view_template(self):
        """Тест шаблона списка историй"""
        response = self.client.get(reverse('recovery_stories:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recovery_stories/list.html')

    def test_stories_list_view_context(self):
        """Тест контекста списка историй"""
        response = self.client.get(reverse('recovery_stories:list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('stories', response.context)
        self.assertIn('categories', response.context)

    def test_stories_list_view_published_filter(self):
        """Тест фильтрации только опубликованных историй"""
        response = self.client.get(reverse('recovery_stories:list'))
        self.assertEqual(response.status_code, 200)
        stories = response.context['stories']
        self.assertIn(self.published_story, stories)
        self.assertNotIn(self.unpublished_story, stories)

    def test_stories_list_view_ordering(self):
        """Тест сортировки историй"""
        # Создаем еще одну историю с более поздней датой
        newer_story = RecoveryStory.objects.create(
            title='Новая история',
            slug='new-story',
            category=self.category,
            author='Аноним',
            content='Новая история...',
            excerpt='Краткое описание',
            is_published=True,
            publish_date=timezone.now() + timezone.timedelta(days=1)
        )
        
        response = self.client.get(reverse('recovery_stories:list'))
        self.assertEqual(response.status_code, 200)
        stories = list(response.context['stories'])
        # Проверяем, что новая история идет первой (по дате публикации)
        self.assertEqual(stories[0], newer_story)

    def test_stories_list_view_empty(self):
        """Тест пустого списка историй"""
        # Удаляем все истории
        RecoveryStory.objects.all().delete()
        
        response = self.client.get(reverse('recovery_stories:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['stories']), 0)

    def test_story_detail_view_template(self):
        """Тест шаблона детальной страницы истории"""
        response = self.client.get(reverse('recovery_stories:detail', kwargs={'slug': self.published_story.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recovery_stories/detail.html')

    def test_story_detail_view_context(self):
        """Тест контекста детальной страницы истории"""
        response = self.client.get(reverse('recovery_stories:detail', kwargs={'slug': self.published_story.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('story', response.context)
        self.assertEqual(response.context['story'], self.published_story)

    def test_story_detail_view_404(self):
        """Тест 404 для несуществующей истории"""
        response = self.client.get(reverse('recovery_stories:detail', kwargs={'slug': 'non-existent-slug'}))
        self.assertEqual(response.status_code, 404)

    def test_story_detail_view_unpublished(self):
        """Тест недоступности неопубликованной истории"""
        response = self.client.get(reverse('recovery_stories:detail', kwargs={'slug': self.unpublished_story.slug}))
        self.assertEqual(response.status_code, 404)

    def test_category_filter_view(self):
        """Тест фильтрации по категории"""
        response = self.client.get(reverse('recovery_stories:category_stories', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recovery_stories/list.html')
        self.assertIn('stories', response.context)
        self.assertIn('current_category', response.context)
        self.assertEqual(response.context['current_category'], self.category)

    def test_tag_filter_view(self):
        """Тест фильтрации по тегу через GET-параметр"""
        response = self.client.get(reverse('recovery_stories:list'), {'tag': self.tag.slug})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recovery_stories/list.html')
        self.assertIn('stories', response.context)
        self.assertIn('active_tag', response.context)
        self.assertEqual(response.context['active_tag'], self.tag.slug) 
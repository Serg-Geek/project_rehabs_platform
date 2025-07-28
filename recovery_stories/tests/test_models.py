from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from recovery_stories.models import RecoveryStory, RecoveryCategory, RecoveryTag
from facilities.models import RehabCenter, OrganizationType
from core.models import City, Region

User = get_user_model()

class RecoveryStoriesModelsTest(TestCase):
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
        
        # Создаем историю
        self.story = RecoveryStory.objects.create(
            title='Мой путь к выздоровлению',
            slug='my-recovery-path',
            category=self.category,
            author='Аноним',
            content='Полная история моего выздоровления...',
            excerpt='Краткое описание истории выздоровления',
            is_published=True,
            publish_date=timezone.now()
        )
        self.story.tags.add(self.tag)

    def test_recovery_category_creation(self):
        self.assertEqual(self.category.name, 'Алкоголизм')
        self.assertEqual(self.category.slug, 'alcoholism')
        self.assertEqual(self.category.description, 'Истории выздоровления от алкоголизма')

    def test_recovery_category_str_representation(self):
        self.assertEqual(str(self.category), 'Алкоголизм')

    def test_recovery_category_verbose_names(self):
        self.assertEqual(RecoveryCategory._meta.verbose_name, 'Категория историй')
        self.assertEqual(RecoveryCategory._meta.verbose_name_plural, 'Категории историй')

    def test_recovery_category_meta_ordering(self):
        self.assertEqual(RecoveryCategory._meta.ordering, ['order', 'name'])

    def test_recovery_story_creation(self):
        self.assertEqual(self.story.title, 'Мой путь к выздоровлению')
        self.assertEqual(self.story.slug, 'my-recovery-path')
        self.assertEqual(self.story.category, self.category)
        self.assertEqual(self.story.author, 'Аноним')
        self.assertTrue(self.story.is_published)

    def test_recovery_story_str_representation(self):
        self.assertEqual(str(self.story), 'Мой путь к выздоровлению')

    def test_recovery_story_verbose_names(self):
        self.assertEqual(RecoveryStory._meta.verbose_name, 'История выздоровления')
        self.assertEqual(RecoveryStory._meta.verbose_name_plural, 'Истории выздоровления')

    def test_recovery_story_meta_ordering(self):
        self.assertEqual(RecoveryStory._meta.ordering, ['-publish_date'])

    def test_recovery_story_published_filter(self):
        unpublished_story = RecoveryStory.objects.create(
            title='Неопубликованная история',
            slug='unpublished-story',
            category=self.category,
            author='Аноним',
            content='Неопубликованная история...',
            excerpt='Краткое описание',
            is_published=False
        )
        
        published_stories = RecoveryStory.objects.filter(is_published=True)
        self.assertIn(self.story, published_stories)
        self.assertNotIn(unpublished_story, published_stories)

    def test_recovery_story_get_absolute_url(self):
        expected_url = f'/recovery-stories/stories/{self.story.slug}/'
        self.assertEqual(self.story.get_absolute_url(), expected_url)

    def test_recovery_tag_creation(self):
        self.assertEqual(self.tag.name, 'Успешное выздоровление')
        self.assertEqual(self.tag.slug, 'successful-recovery')
        self.assertTrue(self.tag.is_active)

    def test_recovery_tag_str_representation(self):
        self.assertEqual(str(self.tag), 'Успешное выздоровление')

    def test_recovery_tag_verbose_names(self):
        self.assertEqual(RecoveryTag._meta.verbose_name, 'Тег историй')
        self.assertEqual(RecoveryTag._meta.verbose_name_plural, 'Теги историй')

    def test_recovery_story_tags_relationship(self):
        self.assertIn(self.tag, self.story.tags.all())
        self.assertEqual(self.story.tags.count(), 1) 
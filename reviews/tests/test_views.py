from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from reviews.models import Review
from facilities.models import Clinic, OrganizationType
from core.models import City, Region

User = get_user_model()

class ReviewsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.region = Region.objects.create(name='Тестовый регион', slug='test-region')
        self.city = City.objects.create(name='Тестовый город', slug='test-city', region=self.region)
        self.organization_type = OrganizationType.objects.create(
            name='Клиника', slug='clinic', description='Медицинская клиника')
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника', city=self.city, address='Тестовый адрес',
            phone='+7 (999) 999-99-99', email='test@test.com', organization_type=self.organization_type)
        self.content_type = ContentType.objects.get_for_model(Clinic)
        self.review1 = Review.objects.create(
            content_type=self.content_type,
            object_id=self.clinic.id,
            created_by=self.user,
            author_name='Иван Иванов',
            author_age=35,
            rating=5,
            content='Очень доволен качеством обслуживания',
            is_published=True
        )
        self.review2 = Review.objects.create(
            content_type=self.content_type,
            object_id=self.clinic.id,
            created_by=self.user,
            author_name='Петр Петров',
            author_age=40,
            rating=4,
            content='Хорошее обслуживание',
            is_published=True
        )

    def test_review_model_creation(self):
        """Тест создания модели Review с существующими полями"""
        self.assertEqual(self.review1.created_by, self.user)
        self.assertEqual(self.review1.rating, 5)
        self.assertEqual(self.review1.author_name, 'Иван Иванов')
        self.assertEqual(self.review1.content, 'Очень доволен качеством обслуживания')
        self.assertTrue(self.review1.is_published)

    def test_review_published_filter(self):
        """Тест фильтрации опубликованных отзывов"""
        unpublished_review = Review.objects.create(
            content_type=self.content_type,
            object_id=self.clinic.id,
            created_by=self.user,
            author_name='Неопубликованный',
            rating=3,
            content='Средне',
            is_published=False
        )
        published_reviews = Review.objects.filter(is_published=True)
        self.assertIn(self.review1, published_reviews)
        self.assertIn(self.review2, published_reviews)
        self.assertNotIn(unpublished_review, published_reviews)

    def test_review_ordering(self):
        """Тест сортировки отзывов"""
        reviews = Review.objects.filter(is_published=True).order_by('-created_at')
        if reviews.count() >= 2:
            self.assertGreaterEqual(reviews[0].created_at, reviews[1].created_at)

    def test_review_empty_list(self):
        """Тест пустого списка отзывов"""
        Review.objects.all().delete()
        reviews = Review.objects.filter(is_published=True)
        self.assertEqual(reviews.count(), 0) 
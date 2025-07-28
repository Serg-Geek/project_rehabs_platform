from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from facilities.models import Clinic, OrganizationType
from core.models import City, Region
from reviews.models import Review

User = get_user_model()

class ReviewsModelsTest(TestCase):
    def setUp(self):
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
        self.review = Review.objects.create(
            content_type=self.content_type,
            object_id=self.clinic.id,
            created_by=self.user,
            author_name='Иван Иванов',
            author_age=35,
            rating=5,
            content='Очень доволен качеством обслуживания',
            is_published=True
        )

    def test_review_creation(self):
        self.assertEqual(self.review.created_by, self.user)
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.author_name, 'Иван Иванов')
        self.assertEqual(self.review.content, 'Очень доволен качеством обслуживания')
        self.assertTrue(self.review.is_published)

    def test_review_str_representation(self):
        # Проверяем строковое представление отзыва
        str_repr = str(self.review)
        self.assertIn(self.review.author_name, str_repr)
        self.assertIn('Отзыв от', str_repr)

    def test_review_rating_validation(self):
        review_min = Review.objects.create(
            content_type=self.content_type,
            object_id=self.clinic.id,
            created_by=self.user,
            author_name='Петр Петров',
            rating=1,
            content='Плохо',
            is_published=True
        )
        self.assertEqual(review_min.rating, 1)
        review_max = Review.objects.create(
            content_type=self.content_type,
            object_id=self.clinic.id,
            created_by=self.user,
            author_name='Сергей Сергеев',
            rating=5,
            content='Отлично',
            is_published=True
        )
        self.assertEqual(review_max.rating, 5)

    def test_review_published_filter(self):
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
        self.assertIn(self.review, published_reviews)
        self.assertNotIn(unpublished_review, published_reviews)

    def test_review_meta_ordering(self):
        self.assertEqual(Review._meta.ordering, ['-created_at'])

    def test_review_verbose_names(self):
        self.assertEqual(Review._meta.verbose_name, 'Отзыв')
        self.assertEqual(Review._meta.verbose_name_plural, 'Отзывы')

    def test_review_field_verbose_names(self):
        rating_field = Review._meta.get_field('rating')
        content_field = Review._meta.get_field('content')
        self.assertEqual(rating_field.verbose_name, 'Оценка')
        self.assertEqual(content_field.verbose_name, 'Текст отзыва') 
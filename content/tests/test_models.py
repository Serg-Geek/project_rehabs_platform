from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from content.models import Banner


class ContentModelsTest(TestCase):
    """Тесты для моделей content приложения"""
    
    def setUp(self):
        """Создаем тестовые данные"""
        today = timezone.now().date()
        
        # Активный баннер
        self.active_banner = Banner.objects.create(
            title='Активный баннер',
            description='Описание активного баннера',
            image='test_image.jpg',
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            order=1,
            is_active=True
        )
        
        # Неактивный баннер
        self.inactive_banner = Banner.objects.create(
            title='Неактивный баннер',
            description='Описание неактивного баннера',
            image='test_image.jpg',
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=1),
            order=2,
            is_active=False
        )
        
        # Будущий баннер
        self.future_banner = Banner.objects.create(
            title='Будущий баннер',
            description='Описание будущего баннера',
            image='test_image.jpg',
            start_date=today + timedelta(days=1),
            end_date=today + timedelta(days=30),
            order=3,
            is_active=True
        )

    def test_banner_creation(self):
        """Тест создания баннера"""
        self.assertEqual(self.active_banner.title, 'Активный баннер')
        self.assertEqual(self.active_banner.description, 'Описание активного баннера')
        self.assertEqual(self.active_banner.image, 'test_image.jpg')
        self.assertTrue(self.active_banner.is_active)
        self.assertEqual(self.active_banner.order, 1)

    def test_banner_str_representation(self):
        """Тест строкового представления баннера"""
        self.assertEqual(str(self.active_banner), 'Активный баннер')

    def test_banner_is_current(self):
        """Тест метода is_current"""
        today = timezone.now().date()
        
        # Активный баннер должен быть текущим
        self.assertTrue(self.active_banner.is_current())
        
        # Неактивный баннер не должен быть текущим
        self.assertFalse(self.inactive_banner.is_current())
        
        # Будущий баннер не должен быть текущим
        self.assertFalse(self.future_banner.is_current())

    def test_banner_ordering(self):
        """Тест сортировки баннеров"""
        banners = Banner.objects.all()
        
        # Проверяем, что баннеры отсортированы по полю order
        self.assertEqual(banners[0].order, 1)  # active_banner
        self.assertEqual(banners[1].order, 2)  # inactive_banner
        self.assertEqual(banners[2].order, 3)  # future_banner

    def test_banner_active_filter(self):
        """Тест фильтрации активных баннеров"""
        active_banners = Banner.objects.filter(is_active=True)
        
        self.assertIn(self.active_banner, active_banners)
        self.assertIn(self.future_banner, active_banners)
        self.assertNotIn(self.inactive_banner, active_banners)

    def test_banner_current_filter(self):
        """Тест фильтрации текущих баннеров"""
        current_banners = [banner for banner in Banner.objects.all() if banner.is_current()]
        
        self.assertIn(self.active_banner, current_banners)
        self.assertNotIn(self.inactive_banner, current_banners)
        self.assertNotIn(self.future_banner, current_banners)

    def test_banner_meta_ordering(self):
        """Тест мета-класса баннера"""
        # Проверяем, что в Meta указана правильная сортировка
        self.assertEqual(Banner._meta.ordering, ['order', '-start_date'])

    def test_banner_verbose_names(self):
        """Тест verbose names баннера"""
        self.assertEqual(Banner._meta.verbose_name, 'Баннер')
        self.assertEqual(Banner._meta.verbose_name_plural, 'Баннеры')

    def test_banner_field_verbose_names(self):
        """Тест verbose names полей баннера"""
        title_field = Banner._meta.get_field('title')
        description_field = Banner._meta.get_field('description')
        image_field = Banner._meta.get_field('image')
        
        self.assertEqual(title_field.verbose_name, 'Заголовок')
        self.assertEqual(description_field.verbose_name, 'Описание')
        self.assertEqual(image_field.verbose_name, 'Изображение') 
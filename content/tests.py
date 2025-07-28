from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from PIL import Image
import io
import os

from .models import Banner
from .validators import (
    validate_image_format, 
    validate_image_dimensions, 
    validate_image_aspect_ratio,
    validate_banner_image,
    validate_desktop_image,
    validate_tablet_image,
    validate_mobile_image,
    get_ratio_display
)
from .constants import DEFAULT_SIZES


class ContentValidatorsTest(TestCase):
    """Тесты для валидаторов изображений"""
    
    def setUp(self):
        """Создаем тестовые изображения"""
        # Создаем тестовое изображение JPEG
        self.create_test_image('test_image.jpg', (800, 600), 'JPEG')
        
        # Создаем тестовое изображение PNG
        self.create_test_image('test_image.png', (1024, 768), 'PNG')
        
        # Создаем маленькое изображение
        self.create_test_image('small_image.jpg', (100, 100), 'JPEG')
        
        # Создаем большое изображение
        self.create_test_image('large_image.jpg', (3000, 2000), 'JPEG')
        
        # Создаем изображение с неправильными пропорциями
        self.create_test_image('wrong_ratio.jpg', (800, 400), 'JPEG')
        
        # Создаем изображение с правильными пропорциями 16:9
        self.create_test_image('correct_ratio.jpg', (1920, 1080), 'JPEG')
    
    def create_test_image(self, filename, size, format):
        """Создает тестовое изображение"""
        img = Image.new('RGB', size, color='red')
        img_io = io.BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        
        setattr(self, filename.replace('.', '_'), SimpleUploadedFile(
            filename, img_io.getvalue(), content_type=f'image/{format.lower()}'
        ))
    
    def test_validate_image_format_valid(self):
        """Тест валидации корректного формата изображения"""
        # Используем структуру из DEFAULT_SIZES
        size = {
            'min_width': 100,
            'min_height': 100,
            'max_width': 2000,
            'max_height': 2000,
            'aspect_ratio': 1.0
        }
        
        # Тестируем JPEG
        validate_image_format(self.test_image_jpg, size)
        self.test_image_jpg.seek(0)
        
        # Тестируем PNG
        validate_image_format(self.test_image_png, size)
        self.test_image_png.seek(0)
    
    def test_validate_image_format_invalid_size(self):
        """Тест валидации изображения с неправильным размером"""
        size = {
            'min_width': 1000,
            'min_height': 1000,
            'max_width': 2000,
            'max_height': 2000,
            'aspect_ratio': 1.0
        }
        
        with self.assertRaises(ValidationError) as context:
            validate_image_format(self.small_image_jpg, size)
        
        self.assertIn('не меньше', str(context.exception))
    
    def test_validate_image_dimensions_valid(self):
        """Тест валидации размеров изображения"""
        validate_image_dimensions(self.test_image_jpg, 100, 100, 2000, 2000)
    
    def test_validate_image_dimensions_too_small(self):
        """Тест валидации слишком маленького изображения"""
        with self.assertRaises(ValidationError) as context:
            validate_image_dimensions(self.small_image_jpg, 200, 200, 2000, 2000)
        
        self.assertIn('слишком маленькое', str(context.exception))
    
    def test_validate_image_dimensions_too_large(self):
        """Тест валидации слишком большого изображения"""
        with self.assertRaises(ValidationError) as context:
            validate_image_dimensions(self.large_image_jpg, 100, 100, 1000, 1000)
        
        self.assertIn('слишком большое', str(context.exception))
    
    def test_validate_image_aspect_ratio_valid(self):
        """Тест валидации правильных пропорций"""
        # 16:9 пропорции
        validate_image_aspect_ratio(self.correct_ratio_jpg, 16/9, tolerance=0.1)
    
    def test_validate_image_aspect_ratio_invalid(self):
        """Тест валидации неправильных пропорций"""
        with self.assertRaises(ValidationError) as context:
            validate_image_aspect_ratio(self.wrong_ratio_jpg, 16/9, tolerance=0.1)
        
        self.assertIn('Неверные пропорции', str(context.exception))
    
    def test_validate_banner_image_desktop_valid(self):
        """Тест валидации баннера для десктопа"""
        validate_banner_image(self.correct_ratio_jpg, 'desktop')
    
    def test_validate_banner_image_desktop_invalid(self):
        """Тест валидации неподходящего баннера для десктопа"""
        with self.assertRaises(ValidationError) as context:
            validate_banner_image(self.small_image_jpg, 'desktop')
        
        # Проверяем, что ошибка содержит информацию о размере
        self.assertIn('не меньше', str(context.exception))
    
    def test_validate_banner_image_invalid_device_type(self):
        """Тест валидации с несуществующим типом устройства"""
        with self.assertRaises(ValidationError) as context:
            validate_banner_image(self.test_image_jpg, 'invalid_device')
        
        self.assertIn('Не найдены форматы', str(context.exception))
    
    def test_validate_desktop_image(self):
        """Тест валидации изображения для десктопа"""
        validate_desktop_image(self.correct_ratio_jpg)
    
    def test_validate_tablet_image(self):
        """Тест валидации изображения для планшета"""
        # Создаем изображение подходящее для планшета
        self.create_test_image('tablet_image.jpg', (1024, 768), 'JPEG')
        validate_tablet_image(self.tablet_image_jpg)
    
    def test_validate_mobile_image(self):
        """Тест валидации изображения для мобильных"""
        # Создаем изображение подходящее для мобильных
        self.create_test_image('mobile_image.jpg', (768, 1024), 'JPEG')
        validate_mobile_image(self.mobile_image_jpg)
    
    def test_get_ratio_display(self):
        """Тест функции отображения пропорций"""
        self.assertEqual(get_ratio_display(1.0), "1:1")
        self.assertEqual(get_ratio_display(3.0), "3:1")
        self.assertEqual(get_ratio_display(16/9), "16:9")
        self.assertEqual(get_ratio_display(9/16), "9:16")
        self.assertEqual(get_ratio_display(4/3), "4:3")
        self.assertEqual(get_ratio_display(3/4), "3:4")
        self.assertEqual(get_ratio_display(2.5), "2.50:1")


class ContentViewsTest(TestCase):
    """Тесты для представлений content приложения"""
    
    def setUp(self):
        """Создаем тестовые данные"""
        self.client = Client()
        
        # Создаем тестовые баннеры
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
    
    def test_home_view_with_banners(self):
        """Тест главной страницы с баннерами"""
        response = self.client.get(reverse('core:home'))
        
        self.assertEqual(response.status_code, 200)
        # Проверяем, что страница загружается без ошибок
        # Баннеры могут быть в контексте или нет, в зависимости от реализации
    
    def test_banner_view_with_banners(self):
        """Тест страницы баннеров"""
        response = self.client.get(reverse('content:banner'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('banners', response.context)
        
        # Проверяем, что только активные баннеры в контексте
        banners = response.context['banners']
        self.assertEqual(len(banners), 1)
        self.assertEqual(banners[0], self.active_banner)
    
    def test_banner_view_no_active_banners(self):
        """Тест страницы баннеров без активных баннеров"""
        # Делаем активный баннер неактивным
        self.active_banner.is_active = False
        self.active_banner.save()
        
        response = self.client.get(reverse('content:banner'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('banners', response.context)
        
        # Проверяем, что нет активных баннеров
        banners = response.context['banners']
        self.assertEqual(len(banners), 0)
    
    def test_banner_view_banners_ordered(self):
        """Тест сортировки баннеров по порядку"""
        # Создаем еще один активный баннер с меньшим порядком
        today = timezone.now().date()
        first_banner = Banner.objects.create(
            title='Первый баннер',
            description='Первый по порядку',
            image='test_image.jpg',
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=30),
            order=0,  # Меньший порядок
            is_active=True
        )
        
        response = self.client.get(reverse('content:banner'))
        banners = response.context['banners']
        
        # Проверяем порядок: first_banner, затем active_banner
        self.assertEqual(banners[0], first_banner)
        self.assertEqual(banners[1], self.active_banner)


class ContentUrlsTest(TestCase):
    """Тесты для URL-ов content приложения"""
    
    def test_banner_url(self):
        """Тест URL для страницы баннеров"""
        url = reverse('content:banner')
        self.assertEqual(url, '/content/banner/')
    
    def test_banner_view_resolves(self):
        """Тест разрешения URL для BannerView"""
        from django.urls import resolve
        from content.views import BannerView
        
        resolver = resolve('/content/banner/')
        self.assertEqual(resolver.func.view_class, BannerView)
        self.assertEqual(resolver.namespace, 'content')
        self.assertEqual(resolver.url_name, 'banner')


class ContentConstantsTest(TestCase):
    """Тесты для констант content приложения"""
    
    def test_default_sizes_structure(self):
        """Тест структуры DEFAULT_SIZES"""
        self.assertIsInstance(DEFAULT_SIZES, list)
        self.assertEqual(len(DEFAULT_SIZES), 3)
        
        # Проверяем наличие всех типов устройств
        device_types = [size['device_type'] for size in DEFAULT_SIZES]
        self.assertIn('desktop', device_types)
        self.assertIn('tablet', device_types)
        self.assertIn('mobile', device_types)
    
    def test_desktop_sizes(self):
        """Тест размеров для десктопа"""
        desktop = next(size for size in DEFAULT_SIZES if size['device_type'] == 'desktop')
        self.assertEqual(desktop['min_width'], 1920)
        self.assertEqual(desktop['min_height'], 1080)
        self.assertEqual(desktop['aspect_ratio'], 16/9)
    
    def test_tablet_sizes(self):
        """Тест размеров для планшета"""
        tablet = next(size for size in DEFAULT_SIZES if size['device_type'] == 'tablet')
        self.assertEqual(tablet['min_width'], 1024)
        self.assertEqual(tablet['min_height'], 768)
        self.assertEqual(tablet['aspect_ratio'], 4/3)
    
    def test_mobile_sizes(self):
        """Тест размеров для мобильных"""
        mobile = next(size for size in DEFAULT_SIZES if size['device_type'] == 'mobile')
        self.assertEqual(mobile['min_width'], 768)
        self.assertEqual(mobile['min_height'], 1024)
        self.assertEqual(mobile['aspect_ratio'], 3/4)

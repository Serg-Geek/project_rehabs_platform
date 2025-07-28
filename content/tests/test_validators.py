from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from PIL import Image
import io

from content.validators import (
    validate_image_format, 
    validate_image_dimensions, 
    validate_image_aspect_ratio,
    validate_banner_image,
    validate_desktop_image,
    validate_tablet_image,
    validate_mobile_image,
    get_ratio_display
)


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

    def test_validate_image_format_invalid_file(self):
        """Тест валидации некорректного файла"""
        # Создаем некорректный файл (не изображение)
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'This is not an image file',
            content_type='text/plain'
        )
        
        size = {
            'min_width': 100,
            'min_height': 100,
            'max_width': 2000,
            'max_height': 2000,
            'aspect_ratio': 1.0
        }
        
        with self.assertRaises(ValidationError) as context:
            validate_image_format(invalid_file, size)
        
        # Исправляем ожидаемое сообщение об ошибке под реальную логику
        self.assertIn('Ошибка при обработке изображения', str(context.exception))

    def test_validate_image_aspect_ratio_tolerance(self):
        """Тест валидации пропорций с разными допусками"""
        # Создаем изображение с пропорциями близкими к 16:9
        self.create_test_image('close_ratio.jpg', (1920, 1081), 'JPEG')  # Очень близко к 16:9
        
        # Должно пройти с большим допуском
        validate_image_aspect_ratio(self.close_ratio_jpg, 16/9, tolerance=0.1)
        
        # Должно не пройти с маленьким допуском
        with self.assertRaises(ValidationError):
            validate_image_aspect_ratio(self.close_ratio_jpg, 16/9, tolerance=0.001) 
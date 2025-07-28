from django.test import TestCase
from content.constants import DEFAULT_SIZES


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

    def test_default_sizes_required_fields(self):
        """Тест обязательных полей в DEFAULT_SIZES"""
        required_fields = ['device_type', 'min_width', 'min_height', 'max_width', 'max_height', 'aspect_ratio']
        
        for size in DEFAULT_SIZES:
            for field in required_fields:
                self.assertIn(field, size)
                self.assertIsNotNone(size[field])

    def test_default_sizes_data_types(self):
        """Тест типов данных в DEFAULT_SIZES"""
        for size in DEFAULT_SIZES:
            self.assertIsInstance(size['device_type'], str)
            self.assertIsInstance(size['min_width'], int)
            self.assertIsInstance(size['min_height'], int)
            self.assertIsInstance(size['max_width'], int)
            self.assertIsInstance(size['max_height'], int)
            self.assertIsInstance(size['aspect_ratio'], (int, float))

    def test_default_sizes_logical_consistency(self):
        """Тест логической согласованности размеров"""
        for size in DEFAULT_SIZES:
            # min_width должно быть меньше max_width
            self.assertLess(size['min_width'], size['max_width'])
            
            # min_height должно быть меньше max_height
            self.assertLess(size['min_height'], size['max_height'])
            
            # aspect_ratio должно быть положительным
            self.assertGreater(size['aspect_ratio'], 0)

    def test_default_sizes_unique_device_types(self):
        """Тест уникальности типов устройств"""
        device_types = [size['device_type'] for size in DEFAULT_SIZES]
        self.assertEqual(len(device_types), len(set(device_types))) 
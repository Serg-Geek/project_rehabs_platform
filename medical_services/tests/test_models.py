from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from medical_services.models import ServiceCategory, Service, TherapyMethod
from core.utils import transliterate


class ServiceCategoryTests(TestCase):
    def setUp(self):
        self.category_data = {
            'name': 'Тестовая категория',
            'description': 'Описание тестовой категории',
            'order': 1,
            'is_active': True
        }

    def test_create_category(self):
        """Тест создания категории услуг"""
        category = ServiceCategory.objects.create(**self.category_data)
        self.assertEqual(category.name, self.category_data['name'])
        # Проверяем, что slug создан (может быть с транслитерацией)
        self.assertIsNotNone(category.slug)
        self.assertGreater(len(category.slug), 0)
        self.assertEqual(category.description, self.category_data['description'])
        self.assertEqual(category.order, self.category_data['order'])
        self.assertTrue(category.is_active)

    def test_category_str_representation(self):
        """Тест строкового представления категории"""
        category = ServiceCategory.objects.create(**self.category_data)
        self.assertEqual(str(category), self.category_data['name'])

    def test_category_ordering(self):
        """Тест сортировки категорий"""
        category1 = ServiceCategory.objects.create(
            name='Категория 1',
            order=2,
            is_active=True
        )
        category2 = ServiceCategory.objects.create(
            name='Категория 2',
            order=1,
            is_active=True
        )
        
        categories = ServiceCategory.objects.all()
        self.assertEqual(list(categories), [category2, category1])

    def test_active_categories_filter(self):
        """Тест фильтрации активных категорий"""
        active_category = ServiceCategory.objects.create(
            name='Активная категория',
            is_active=True
        )
        inactive_category = ServiceCategory.objects.create(
            name='Неактивная категория',
            is_active=False
        )
        
        active_categories = ServiceCategory.objects.filter(is_active=True)
        self.assertIn(active_category, active_categories)
        self.assertNotIn(inactive_category, active_categories)


class ServiceTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name='Тестовая категория',
            description='Описание тестовой категории',
            is_active=True
        )
        self.service_data = {
            'name': 'Тестовая услуга',
            'description': 'Описание тестовой услуги',
            'is_active': True,
            'display_priority': 1
        }

    def test_create_service(self):
        """Тест создания услуги"""
        service = Service.objects.create(**self.service_data)
        self.assertEqual(service.name, self.service_data['name'])
        # Проверяем, что slug создан (может быть с транслитерацией)
        self.assertIsNotNone(service.slug)
        self.assertGreater(len(service.slug), 0)
        self.assertEqual(service.description, self.service_data['description'])
        self.assertTrue(service.is_active)
        self.assertEqual(service.display_priority, self.service_data['display_priority'])

    def test_service_str_representation(self):
        """Тест строкового представления услуги"""
        service = Service.objects.create(**self.service_data)
        self.assertEqual(str(service), self.service_data['name'])

    def test_service_categories_relationship(self):
        """Тест связи услуги с категориями"""
        service = Service.objects.create(**self.service_data)
        service.categories.add(self.category)
        
        self.assertIn(self.category, service.categories.all())
        self.assertIn(service, self.category.services.all())

    def test_service_priority_ordering(self):
        """Тест сортировки услуг по приоритету"""
        service1 = Service.objects.create(
            name='Услуга 1',
            display_priority=1,
            is_active=True
        )
        service2 = Service.objects.create(
            name='Услуга 2',
            display_priority=3,
            is_active=True
        )
        service3 = Service.objects.create(
            name='Услуга 3',
            display_priority=2,
            is_active=True
        )
        
        services = Service.objects.order_by('-display_priority')
        self.assertEqual(list(services), [service2, service3, service1])

    def test_active_services_filter(self):
        """Тест фильтрации активных услуг"""
        active_service = Service.objects.create(
            name='Активная услуга',
            is_active=True
        )
        inactive_service = Service.objects.create(
            name='Неактивная услуга',
            is_active=False
        )
        
        active_services = Service.objects.filter(is_active=True)
        self.assertIn(active_service, active_services)
        self.assertNotIn(inactive_service, active_services)

    def test_service_rehabilitation_program_flag(self):
        """Тест флага реабилитационной программы"""
        service = Service.objects.create(
            name='Реабилитационная программа',
            is_rehabilitation_program=True,
            is_active=True
        )
        self.assertTrue(service.is_rehabilitation_program)

    def test_service_seo_fields(self):
        """Тест SEO полей услуги"""
        service = Service.objects.create(
            name='Услуга с SEO',
            meta_title='SEO заголовок',
            meta_description='SEO описание',
            is_active=True
        )
        self.assertEqual(service.meta_title, 'SEO заголовок')
        self.assertEqual(service.meta_description, 'SEO описание')


class TherapyMethodTests(TestCase):
    def setUp(self):
        self.method_data = {
            'name': 'Тестовый метод терапии',
            'description': 'Описание тестового метода',
            'is_active': True
        }

    def test_create_therapy_method(self):
        """Тест создания метода терапии"""
        method = TherapyMethod.objects.create(**self.method_data)
        self.assertEqual(method.name, self.method_data['name'])
        # Проверяем, что slug создан (может быть с транслитерацией)
        self.assertIsNotNone(method.slug)
        self.assertGreater(len(method.slug), 0)
        self.assertEqual(method.description, self.method_data['description'])
        self.assertTrue(method.is_active)

    def test_therapy_method_str_representation(self):
        """Тест строкового представления метода терапии"""
        method = TherapyMethod.objects.create(**self.method_data)
        self.assertEqual(str(method), self.method_data['name'])

    def test_active_therapy_methods_filter(self):
        """Тест фильтрации активных методов терапии"""
        active_method = TherapyMethod.objects.create(
            name='Активный метод',
            is_active=True
        )
        inactive_method = TherapyMethod.objects.create(
            name='Неактивный метод',
            is_active=False
        )
        
        active_methods = TherapyMethod.objects.filter(is_active=True)
        self.assertIn(active_method, active_methods)
        self.assertNotIn(inactive_method, active_methods) 
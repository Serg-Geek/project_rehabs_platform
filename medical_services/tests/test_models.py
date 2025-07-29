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


class ServiceCategoryModelsTest(TestCase):
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем категорию
        self.category = ServiceCategory.objects.create(
            name='Тестовая категория',
            slug='test-category',
            description='Описание тестовой категории'
        )
        
        # Создаем активную услугу
        self.active_service = Service.objects.create(
            name='Активная услуга',
            slug='active-service',
            description='Описание активной услуги',
            is_active=True
        )
        self.active_service.categories.add(self.category)
        
        # Создаем неактивную услугу
        self.inactive_service = Service.objects.create(
            name='Неактивная услуга',
            slug='inactive-service',
            description='Описание неактивной услуги',
            is_active=False
        )
        self.inactive_service.categories.add(self.category)

    def test_service_category_str_representation(self):
        """Тест строкового представления категории"""
        self.assertEqual(str(self.category), 'Тестовая категория')

    def test_service_category_active_services_method(self):
        """Тест метода active_services для получения только активных услуг"""
        # Проверяем, что метод возвращает только активные услуги
        active_services = self.category.active_services()
        self.assertIn(self.active_service, active_services)
        self.assertNotIn(self.inactive_service, active_services)
        self.assertEqual(active_services.count(), 1)
        
        # Проверяем сортировку по приоритету и названию
        self.assertEqual(active_services.first(), self.active_service)

    def test_active_services_empty_result(self):
        """Тест метода active_services когда нет активных услуг"""
        # Делаем все услуги неактивными
        self.active_service.is_active = False
        self.active_service.save()
        
        # Проверяем, что метод возвращает пустой QuerySet
        active_services = self.category.active_services()
        self.assertEqual(active_services.count(), 0)
        self.assertNotIn(self.active_service, active_services)
        self.assertNotIn(self.inactive_service, active_services)

    def test_active_services_sorting(self):
        """Тест сортировки услуг по приоритету и названию"""
        # Создаем услуги с разными приоритетами
        high_priority_service = Service.objects.create(
            name='Высокий приоритет',
            slug='high-priority',
            display_priority=Service.PRIORITY_HIGH,
            is_active=True
        )
        high_priority_service.categories.add(self.category)
        
        low_priority_service = Service.objects.create(
            name='Низкий приоритет',
            slug='low-priority',
            display_priority=Service.PRIORITY_LOW,
            is_active=True
        )
        low_priority_service.categories.add(self.category)
        
        # Проверяем сортировку (высокий приоритет должен быть первым)
        active_services = list(self.category.active_services())
        self.assertEqual(active_services[0], high_priority_service)  # Высокий приоритет
        self.assertEqual(active_services[1], self.active_service)    # Средний приоритет
        self.assertEqual(active_services[2], low_priority_service)   # Низкий приоритет

    def test_active_services_cross_category_isolation(self):
        """Тест изоляции услуг между разными категориями"""
        # Создаем вторую категорию
        second_category = ServiceCategory.objects.create(
            name='Вторая категория',
            slug='second-category',
            description='Описание второй категории'
        )
        
        # Создаем услугу для второй категории
        second_category_service = Service.objects.create(
            name='Услуга второй категории',
            slug='second-category-service',
            is_active=True
        )
        second_category_service.categories.add(second_category)
        
        # Проверяем, что каждый метод возвращает только свои услуги
        first_category_services = self.category.active_services()
        second_category_services = second_category.active_services()
        
        self.assertIn(self.active_service, first_category_services)
        self.assertNotIn(second_category_service, first_category_services)
        
        self.assertIn(second_category_service, second_category_services)
        self.assertNotIn(self.active_service, second_category_services) 
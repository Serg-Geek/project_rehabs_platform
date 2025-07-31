from django.test import TestCase, Client
from django.urls import reverse
from medical_services.models import ServiceCategory, Service


class HomePageServicesTest(TestCase):
    """Тесты для проверки отображения категорий услуг на главной странице"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.client = Client()
        self.home_url = reverse('core:home')
        
        # Создаем категории услуг
        self.alcoholism_category = ServiceCategory.objects.create(
            name='Лечение алкоголизма',
            slug='lechenie-alkogolizma',
            description='Комплексное лечение алкогольной зависимости',
            order=1,
            is_active=True
        )
        
        self.drug_addiction_category = ServiceCategory.objects.create(
            name='Лечение наркомании',
            slug='lechenie-narkomanii',
            description='Комплексное лечение наркотической зависимости',
            order=2,
            is_active=True
        )
        
        self.other_category = ServiceCategory.objects.create(
            name='Другие услуги',
            slug='drugie-uslugi',
            description='Дополнительные услуги по лечению зависимостей',
            order=3,
            is_active=True
        )
        
        # Создаем услуги для каждой категории
        self.alcoholism_services = [
            Service.objects.create(
                name='Реабилитация',
                description='Услуга по лечению алкоголизма: Реабилитация',
                is_active=True
            ),
            Service.objects.create(
                name='Детоксикация',
                description='Услуга по лечению алкоголизма: Детоксикация',
                is_active=True
            )
        ]
        
        self.drug_addiction_services = [
            Service.objects.create(
                name='Реабилитация',
                description='Услуга по лечению наркомании: Реабилитация',
                is_active=True
            ),
            Service.objects.create(
                name='Детоксикация',
                description='Услуга по лечению наркомании: Детоксикация',
                is_active=True
            )
        ]
        
        self.other_services = [
            Service.objects.create(
                name='Психологическая помощь',
                description='Дополнительная услуга: Психологическая помощь',
                is_active=True
            ),
            Service.objects.create(
                name='Психиатрическая помощь',
                description='Дополнительная услуга: Психиатрическая помощь',
                is_active=True
            )
        ]
        
        # Добавляем услуги в категории
        for service in self.alcoholism_services:
            service.categories.add(self.alcoholism_category)
            
        for service in self.drug_addiction_services:
            service.categories.add(self.drug_addiction_category)
            
        for service in self.other_services:
            service.categories.add(self.other_category)
    
    def test_home_page_returns_200(self):
        """Проверка доступности главной страницы"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
    
    def test_service_categories_in_context(self):
        """Проверка наличия категорий услуг в контексте"""
        response = self.client.get(self.home_url)
        self.assertIn('service_categories', response.context)
        
        service_categories = response.context['service_categories']
        # Проверяем, что это список и содержит наши категории
        self.assertIsInstance(service_categories, list)
        self.assertIn(self.alcoholism_category, service_categories)
        self.assertIn(self.drug_addiction_category, service_categories)
        self.assertIn(self.other_category, service_categories)
    
    def test_alcoholism_category_content(self):
        """Проверка содержимого категории лечения алкоголизма"""
        response = self.client.get(self.home_url)
        service_categories = list(response.context['service_categories'])
        
        # Получаем категорию из списка
        alcoholism_category = next((cat for cat in service_categories if cat.slug == 'lechenie-alkogolizma'), None)
        self.assertEqual(alcoholism_category, self.alcoholism_category)
        
        # Проверяем услуги категории
        alcoholism_services = alcoholism_category.services.filter(is_active=True)
        self.assertEqual(set(alcoholism_services), set(self.alcoholism_services))
    
    def test_drug_addiction_category_content(self):
        """Проверка содержимого категории лечения наркомании"""
        response = self.client.get(self.home_url)
        service_categories = list(response.context['service_categories'])
        
        # Получаем категорию из списка
        drug_addiction_category = next((cat for cat in service_categories if cat.slug == 'lechenie-narkomanii'), None)
        self.assertEqual(drug_addiction_category, self.drug_addiction_category)
        
        # Проверяем услуги категории
        drug_addiction_services = drug_addiction_category.services.filter(is_active=True)
        self.assertEqual(set(drug_addiction_services), set(self.drug_addiction_services))
    
    def test_other_category_content(self):
        """Проверка содержимого категории других услуг"""
        response = self.client.get(self.home_url)
        service_categories = list(response.context['service_categories'])
        
        # Получаем категорию из списка
        other_category = next((cat for cat in service_categories if cat.slug == 'drugie-uslugi'), None)
        self.assertEqual(other_category, self.other_category)
        
        # Проверяем услуги категории
        other_services = other_category.services.filter(is_active=True)
        self.assertEqual(set(other_services), set(self.other_services))
    
    def test_inactive_services_not_included(self):
        """Проверка, что неактивные услуги не включаются в список"""
        # Создаем неактивную услугу
        inactive_service = Service.objects.create(
            name='Неактивная услуга',
            description='Неактивная услуга',
            is_active=False
        )
        inactive_service.categories.add(self.alcoholism_category)
        
        response = self.client.get(self.home_url)
        service_categories = list(response.context['service_categories'])
        alcoholism_category = next((cat for cat in service_categories if cat.slug == 'lechenie-alkogolizma'), None)
        alcoholism_services = alcoholism_category.services.filter(is_active=True)
        
        self.assertNotIn(inactive_service, alcoholism_services)
    
    def test_inactive_category_not_included(self):
        """Проверка, что неактивные категории не включаются в список"""
        # Делаем категорию неактивной
        self.alcoholism_category.is_active = False
        self.alcoholism_category.save()
        
        response = self.client.get(self.home_url)
        service_categories = response.context['service_categories']
        
        self.assertNotIn(self.alcoholism_category, service_categories)


class ServiceDisplayOrderTest(TestCase):
    """Тест сортировки услуг по порядку отображения"""
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')
        self.category = ServiceCategory.objects.create(
            name='Тестовая категория',
            slug='lechenie-alkogolizma',  # Ключ для главной страницы
            description='Тест',
            order=1,
            is_active=True
        )
        self.service_first = Service.objects.create(
            name='Первая услуга',
            description='Услуга с первым порядком',
            is_active=True,
            display_order=1
        )
        self.service_second = Service.objects.create(
            name='Вторая услуга',
            description='Услуга со вторым порядком',
            is_active=True,
            display_order=2
        )
        self.service_third = Service.objects.create(
            name='Третья услуга',
            description='Услуга с третьим порядком',
            is_active=True,
            display_order=3
        )
        for s in [self.service_first, self.service_second, self.service_third]:
            s.categories.add(self.category)

    def test_services_order_by_display_order(self):
        response = self.client.get(self.home_url)
        service_categories = list(response.context['service_categories'])
        category = next((cat for cat in service_categories if cat.slug == 'lechenie-alkogolizma'), None)
        services = category.services.filter(is_active=True).order_by('display_order')
        # Проверяем порядок: первый, второй, третий
        self.assertEqual(list(services), [self.service_first, self.service_second, self.service_third]) 
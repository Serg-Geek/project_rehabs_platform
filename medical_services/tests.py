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
                duration=60,
                is_active=True
            ),
            Service.objects.create(
                name='Детоксикация',
                description='Услуга по лечению алкоголизма: Детоксикация',
                duration=60,
                is_active=True
            )
        ]
        
        self.drug_addiction_services = [
            Service.objects.create(
                name='Реабилитация',
                description='Услуга по лечению наркомании: Реабилитация',
                duration=60,
                is_active=True
            ),
            Service.objects.create(
                name='Детоксикация',
                description='Услуга по лечению наркомании: Детоксикация',
                duration=60,
                is_active=True
            )
        ]
        
        self.other_services = [
            Service.objects.create(
                name='Психологическая помощь',
                description='Дополнительная услуга: Психологическая помощь',
                duration=60,
                is_active=True
            ),
            Service.objects.create(
                name='Психиатрическая помощь',
                description='Дополнительная услуга: Психиатрическая помощь',
                duration=60,
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
        self.assertIn('alcoholism', service_categories)
        self.assertIn('drug_addiction', service_categories)
        self.assertIn('other', service_categories)
    
    def test_alcoholism_category_content(self):
        """Проверка содержимого категории лечения алкоголизма"""
        response = self.client.get(self.home_url)
        alcoholism_data = response.context['service_categories']['alcoholism']
        
        self.assertEqual(alcoholism_data['category'], self.alcoholism_category)
        self.assertEqual(
            set(alcoholism_data['services']),
            set(self.alcoholism_services)
        )
    
    def test_drug_addiction_category_content(self):
        """Проверка содержимого категории лечения наркомании"""
        response = self.client.get(self.home_url)
        drug_addiction_data = response.context['service_categories']['drug_addiction']
        
        self.assertEqual(drug_addiction_data['category'], self.drug_addiction_category)
        self.assertEqual(
            set(drug_addiction_data['services']),
            set(self.drug_addiction_services)
        )
    
    def test_other_category_content(self):
        """Проверка содержимого категории других услуг"""
        response = self.client.get(self.home_url)
        other_data = response.context['service_categories']['other']
        
        self.assertEqual(other_data['category'], self.other_category)
        self.assertEqual(
            set(other_data['services']),
            set(self.other_services)
        )
    
    def test_inactive_services_not_included(self):
        """Проверка, что неактивные услуги не включаются в список"""
        # Создаем неактивную услугу
        inactive_service = Service.objects.create(
            name='Неактивная услуга',
            description='Неактивная услуга',
            duration=60,
            is_active=False
        )
        inactive_service.categories.add(self.alcoholism_category)
        
        response = self.client.get(self.home_url)
        alcoholism_services = response.context['service_categories']['alcoholism']['services']
        
        self.assertNotIn(inactive_service, alcoholism_services)
    
    def test_inactive_category_not_included(self):
        """Проверка, что неактивные категории не включаются в список"""
        # Делаем категорию неактивной
        self.alcoholism_category.is_active = False
        self.alcoholism_category.save()
        
        response = self.client.get(self.home_url)
        service_categories = response.context['service_categories']
        
        self.assertNotIn('alcoholism', service_categories)

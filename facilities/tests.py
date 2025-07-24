from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from facilities.models import RehabCenter
from medical_services.models import Service, ServiceCategory, FacilityService

# Create your tests here.

class RehabCenterServicesPriorityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = ServiceCategory.objects.create(
            name='Тестовая категория',
            slug='test-category',
            description='Тест',
            order=1,
            is_active=True
        )
        self.center = RehabCenter.objects.create(
            name='Тестовый центр',
            slug='test-center',
            organization_type_id=1,
            description='Тест',
            address='Тест',
            phone='123',
            is_active=True
        )
        self.service_high = Service.objects.create(
            name='Высокий приоритет',
            description='Услуга с высоким приоритетом',
            duration=30,
            is_active=True,
            display_priority=3
        )
        self.service_medium = Service.objects.create(
            name='Средний приоритет',
            description='Услуга со средним приоритетом',
            duration=30,
            is_active=True,
            display_priority=2
        )
        self.service_low = Service.objects.create(
            name='Низкий приоритет',
            description='Услуга с низким приоритетом',
            duration=30,
            is_active=True,
            display_priority=1
        )
        for s in [self.service_high, self.service_medium, self.service_low]:
            s.categories.add(self.category)
            FacilityService.objects.create(
                content_type=ContentType.objects.get_for_model(self.center),
                object_id=self.center.pk,
                service=s,
                is_active=True
            )

    def test_services_order_by_priority_on_detail(self):
        url = reverse('facilities:facility_detail', kwargs={'facility_type': 'rehab', 'slug': self.center.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        services = response.context['services']
        # Проверяем порядок: высокий, средний, низкий
        ordered_services = [fs.service for fs in services]
        self.assertEqual(ordered_services, [self.service_high, self.service_medium, self.service_low])

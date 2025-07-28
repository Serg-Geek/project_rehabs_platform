from django.test import TestCase, Client
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.contrib.auth import get_user_model

from staff.models import MedicalSpecialist, FacilitySpecialist, Specialization
from facilities.models import Clinic, OrganizationType
from core.models import City, Region

User = get_user_model()


class StaffViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Создаем тестовые данные
        self.region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region'
        )
        self.city = City.objects.create(
            name='Тестовый город',
            slug='test-city',
            region=self.region
        )
        
        self.organization_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic',
            description='Медицинская клиника'
        )
        
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника',
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            organization_type=self.organization_type
        )
        
        self.specialization = Specialization.objects.create(
            name='Терапевт',
            description='Врач общей практики'
        )
        
        # Создаем FacilitySpecialist (представления работают только с ним)
        clinic_type = ContentType.objects.get_for_model(Clinic)
        self.facility_specialist = FacilitySpecialist.objects.create(
            first_name='Петр',
            last_name='Петров',
            middle_name='Петрович',
            slug='petrov-petr',
            is_active=True,
            content_type=clinic_type,
            object_id=self.clinic.id,
            position='Главный врач',
            experience_years=5,
            education='Высшее медицинское'
        )
        self.facility_specialist.specializations.add(self.specialization)
        
        # Создаем еще одного FacilitySpecialist для тестов
        self.facility_specialist2 = FacilitySpecialist.objects.create(
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович',
            slug='ivanov-ivan',
            is_active=True,
            content_type=clinic_type,
            object_id=self.clinic.id,
            position='Врач',
            experience_years=3,
            education='Высшее медицинское'
        )
        self.facility_specialist2.specializations.add(self.specialization)

    def test_specialists_list_view(self):
        """Тест представления списка специалистов"""
        response = self.client.get(reverse('staff:specialists_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/specialists_list.html')
        
        # Проверяем, что специалисты в контексте
        self.assertIn('specialists', response.context)
        specialists = response.context['specialists']
        # В списке должны быть только FacilitySpecialist
        self.assertIn(self.facility_specialist, specialists)
        self.assertIn(self.facility_specialist2, specialists)

    def test_specialist_detail_view(self):
        """Тест представления детальной страницы специалиста"""
        response = self.client.get(reverse('staff:specialist_detail', kwargs={
            'slug': self.facility_specialist.slug
        }))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/specialist_detail.html')
        
        # Проверяем, что специалист в контексте
        self.assertIn('specialist', response.context)
        self.assertEqual(response.context['specialist'], self.facility_specialist)

    def test_specialist_detail_view_404(self):
        """Тест 404 для несуществующего специалиста"""
        response = self.client.get(reverse('staff:specialist_detail', kwargs={
            'slug': 'non-existent-slug'
        }))
        self.assertEqual(response.status_code, 404)

    def test_specialists_list_view_search(self):
        """Тест поиска в списке специалистов"""
        response = self.client.get(reverse('staff:specialists_list'), {
            'search': 'Петров'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/specialists_list.html')
        
        # Проверяем, что найденные специалисты в контексте
        self.assertIn('specialists', response.context)
        specialists = response.context['specialists']
        self.assertIn(self.facility_specialist, specialists)
        self.assertNotIn(self.facility_specialist2, specialists)

    def test_specialists_list_view_search_by_position(self):
        """Тест поиска по должности"""
        response = self.client.get(reverse('staff:specialists_list'), {
            'search': 'Главный врач'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/specialists_list.html')
        
        # Проверяем, что найденные специалисты в контексте
        self.assertIn('specialists', response.context)
        specialists = response.context['specialists']
        self.assertIn(self.facility_specialist, specialists)
        self.assertNotIn(self.facility_specialist2, specialists)

    def test_specialists_list_view_empty_search(self):
        """Тест поиска с пустым запросом"""
        response = self.client.get(reverse('staff:specialists_list'), {
            'search': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/specialists_list.html')
        
        # При пустом запросе должны быть все специалисты
        self.assertIn('specialists', response.context)
        specialists = response.context['specialists']
        self.assertIn(self.facility_specialist, specialists)
        self.assertIn(self.facility_specialist2, specialists)

    def test_specialists_list_view_no_results(self):
        """Тест поиска без результатов"""
        response = self.client.get(reverse('staff:specialists_list'), {
            'search': 'НесуществующийСпециалист'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/specialists_list.html')
        
        # При поиске несуществующего специалиста список должен быть пустым
        self.assertIn('specialists', response.context)
        specialists = response.context['specialists']
        self.assertEqual(len(specialists), 0) 
"""
Тесты для представлений медицинских учреждений.

Этот модуль содержит тесты для проверки функциональности:
- AJAX views (load_more_rehabs, load_more_clinics, load_more_doctors)
- PrivateDoctorListView и PrivateDoctorDetailView
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from facilities.models import Clinic, RehabCenter, PrivateDoctor, OrganizationType
from staff.models import Specialization
from core.models import Region, City
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class AjaxViewsTest(TestCase):
    """Тесты для AJAX views (load_more)"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.client = Client()
        
        # Создаем регион и город
        self.region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region-ajax'
        )
        self.city = City.objects.create(
            name='Тестовый город',
            slug='test-city-ajax',
            region=self.region
        )
        
        # Создаем типы организаций
        self.clinic_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic-ajax',
            description='Описание клиники',
            competencies='Компетенции клиники'
        )
        self.rehab_type = OrganizationType.objects.create(
            name='Реабилитационный центр',
            slug='rehabilitation-ajax',
            description='Описание центра',
            competencies='Компетенции центра'
        )
        
        # Создаем тестовые учреждения
        for i in range(15):
            Clinic.objects.create(
                name=f'Клиника {i}',
                slug=f'clinic-{i}-ajax',
                organization_type=self.clinic_type,
                city=self.city,
                address=f'Адрес {i}',
                phone=f'+7 (999) 999-99-{i:02d}',
                description=f'Описание {i}'
            )
            
            RehabCenter.objects.create(
                name=f'Центр {i}',
                slug=f'rehab-{i}-ajax',
                organization_type=self.rehab_type,
                city=self.city,
                address=f'Адрес {i}',
                phone=f'+7 (999) 999-98-{i:02d}',
                description=f'Описание {i}'
            )
    
    def test_load_more_clinics_success(self):
        """Тест успешной загрузки дополнительных клиник"""
        response = self.client.get(reverse('facilities:load_more_clinics'), {
            'offset': 0
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('cards', data)
        self.assertIn('has_more', data)
        self.assertTrue(data['has_more'])  # Должно быть больше клиник
        self.assertIsInstance(data['cards'], str)
        self.assertGreater(len(data['cards']), 0)
    
    def test_load_more_clinics_with_offset(self):
        """Тест загрузки клиник с offset"""
        response = self.client.get(reverse('facilities:load_more_clinics'), {
            'offset': 10
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('cards', data)
        self.assertIn('has_more', data)
        self.assertIsInstance(data['cards'], str)
    
    def test_load_more_clinics_invalid_offset(self):
        """Тест загрузки клиник с некорректным offset"""
        response = self.client.get(reverse('facilities:load_more_clinics'), {
            'offset': 'invalid'
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_load_more_rehabs_success(self):
        """Тест успешной загрузки дополнительных реабилитационных центров"""
        response = self.client.get(reverse('facilities:load_more_rehabs'), {
            'offset': 0
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('cards', data)
        self.assertIn('has_more', data)
        self.assertTrue(data['has_more'])  # Должно быть больше центров
        self.assertIsInstance(data['cards'], str)
        self.assertGreater(len(data['cards']), 0)
    
    def test_load_more_rehabs_with_offset(self):
        """Тест загрузки реабилитационных центров с offset"""
        response = self.client.get(reverse('facilities:load_more_rehabs'), {
            'offset': 10
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('cards', data)
        self.assertIn('has_more', data)
        self.assertIsInstance(data['cards'], str)
    
    def test_load_more_rehabs_invalid_offset(self):
        """Тест загрузки реабилитационных центров с некорректным offset"""
        response = self.client.get(reverse('facilities:load_more_rehabs'), {
            'offset': 'invalid'
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)


class PrivateDoctorViewsTest(TestCase):
    """Тесты для PrivateDoctorListView и PrivateDoctorDetailView"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.client = Client()
        
        # Создаем регион и город
        self.region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region-doctor'
        )
        self.city = City.objects.create(
            name='Тестовый город',
            slug='test-city-doctor',
            region=self.region
        )
        
        # Создаем специализации
        self.specialization1 = Specialization.objects.create(
            name='Наркология',
            slug='narkologiya-doctor',
            description='Лечение наркомании'
        )
        self.specialization2 = Specialization.objects.create(
            name='Психиатрия',
            slug='psihiatriya-doctor',
            description='Психиатрическая помощь'
        )
        
        # Создаем типы организаций
        self.doctor_type = OrganizationType.objects.create(
            name='Частный врач',
            slug='private-doctor-test',
            description='Описание частного врача',
            competencies='Компетенции врача'
        )
        
        # Создаем тестовых врачей
        self.doctor1 = PrivateDoctor.objects.create(
            name='Доктор Иванов',
            slug='doctor-ivanov-test',
            organization_type=self.doctor_type,
            city=self.city,
            address='Адрес врача 1',
            phone='+7 (999) 111-11-11',
            first_name='Иван',
            last_name='Иванов',
            experience_years=10,
            schedule='Пн-Пт 9:00-18:00',
            home_visits=True,
            consultation_price=5000.00
        )
        self.doctor1.specializations.add(self.specialization1)
        
        self.doctor2 = PrivateDoctor.objects.create(
            name='Доктор Петров',
            slug='doctor-petrov-test',
            organization_type=self.doctor_type,
            city=self.city,
            address='Адрес врача 2',
            phone='+7 (999) 222-22-22',
            first_name='Петр',
            last_name='Петров',
            experience_years=15,
            schedule='Пн-Сб 10:00-19:00',
            home_visits=False,
            consultation_price=7000.00
        )
        self.doctor2.specializations.add(self.specialization2)
    
    def test_private_doctor_list_view(self):
        """Тест отображения списка частных врачей"""
        response = self.client.get(reverse('facilities:private_doctors_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('doctors', response.context)
        
        doctors = response.context['doctors']
        doctor_names = [d.name for d in doctors]
        self.assertIn(self.doctor1.name, doctor_names)
        self.assertIn(self.doctor2.name, doctor_names)
    
    def test_private_doctor_list_view_search(self):
        """Тест поиска в списке частных врачей"""
        response = self.client.get(reverse('facilities:private_doctors_list'), {
            'search': 'Иванов'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('doctors', response.context)
        
        doctors = response.context['doctors']
        doctor_names = [d.name for d in doctors]
        self.assertIn(self.doctor1.name, doctor_names)
        self.assertNotIn(self.doctor2.name, doctor_names)
    
    def test_private_doctor_list_view_filter_city(self):
        """Тест фильтрации по городу"""
        response = self.client.get(reverse('facilities:private_doctors_list'), {
            'city': self.city.slug
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('doctors', response.context)
        
        doctors = response.context['doctors']
        self.assertEqual(len(doctors), 2)
    
    def test_private_doctor_list_view_filter_specialization(self):
        """Тест фильтрации по специализации"""
        response = self.client.get(reverse('facilities:private_doctors_list'), {
            'specialization': self.specialization1.slug
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('doctors', response.context)
        
        doctors = response.context['doctors']
        doctor_names = [d.name for d in doctors]
        self.assertIn(self.doctor1.name, doctor_names)
        self.assertNotIn(self.doctor2.name, doctor_names)
    
    def test_private_doctor_list_view_filter_home_visits(self):
        """Тест фильтрации по выезду на дом"""
        response = self.client.get(reverse('facilities:private_doctors_list'), {
            'home_visits': True
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('doctors', response.context)
        
        doctors = response.context['doctors']
        doctor_names = [d.name for d in doctors]
        self.assertIn(self.doctor1.name, doctor_names)
        self.assertNotIn(self.doctor2.name, doctor_names)
    
    def test_private_doctor_list_view_seo_context(self):
        """Тест SEO контекста в списке врачей"""
        response = self.client.get(reverse('facilities:private_doctors_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('meta_title', response.context)
        self.assertIn('meta_description', response.context)
        
        self.assertIn('Частные врачи', response.context['meta_title'])
        self.assertIn('врачи-наркологи', response.context['meta_description'])
    
    def test_private_doctor_detail_view(self):
        """Тест детального просмотра частного врача"""
        response = self.client.get(reverse('facilities:private_doctor_detail', kwargs={
            'slug': self.doctor1.slug
        }))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('doctor', response.context)
        
        doctor = response.context['doctor']
        self.assertEqual(doctor, self.doctor1)
    
    def test_private_doctor_detail_view_invalid_slug(self):
        """Тест детального просмотра с неверным slug"""
        response = self.client.get(reverse('facilities:private_doctor_detail', kwargs={
            'slug': 'invalid-slug'
        }))
        
        self.assertEqual(response.status_code, 404)
    
    def test_private_doctor_detail_view_seo_context(self):
        """Тест SEO контекста в детальном просмотре врача"""
        response = self.client.get(reverse('facilities:private_doctor_detail', kwargs={
            'slug': self.doctor1.slug
        }))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('meta_title', response.context)
        self.assertIn('meta_description', response.context)
        
        # Проверяем, что meta_title содержит имя врача
        self.assertIn(self.doctor1.get_full_name(), response.context['meta_title'])
    
    def test_load_more_doctors_success(self):
        """Тест успешной загрузки дополнительных врачей"""
        response = self.client.get(reverse('facilities:load_more_doctors'), {
            'offset': 0
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('cards', data)
        self.assertIn('has_more', data)
        self.assertIsInstance(data['cards'], str)
        self.assertGreater(len(data['cards']), 0)
    
    def test_load_more_doctors_with_offset(self):
        """Тест загрузки врачей с offset"""
        response = self.client.get(reverse('facilities:load_more_doctors'), {
            'offset': 1
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('cards', data)
        self.assertIn('has_more', data)
        self.assertIsInstance(data['cards'], str)
    
    def test_load_more_doctors_invalid_offset(self):
        """Тест загрузки врачей с некорректным offset"""
        response = self.client.get(reverse('facilities:load_more_doctors'), {
            'offset': 'invalid'
        })
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data) 
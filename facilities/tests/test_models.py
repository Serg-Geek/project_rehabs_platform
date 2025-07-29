from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from facilities.models import Clinic, RehabCenter, OrganizationType
from staff.models import FacilitySpecialist
from core.models import City, Region


class FacilityModelsTest(TestCase):
    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем регион и город
        self.region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region'
        )
        self.city = City.objects.create(
            name='Тестовый город',
            slug='test-city',
            region=self.region
        )
        
        # Создаем тип организации
        self.organization_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic',
            description='Медицинская клиника',
            competencies='Лечение зависимостей'
        )
        
        # Создаем клинику
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника',
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            organization_type=self.organization_type
        )
        
        # Создаем реабилитационный центр
        self.rehab_center = RehabCenter.objects.create(
            name='Тестовый центр',
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            organization_type=self.organization_type
        )

    def test_clinic_str_representation(self):
        """Тест строкового представления клиники"""
        expected = f'Тестовая клиника (Клиника) [ID: {self.clinic.id}]'
        self.assertEqual(str(self.clinic), expected)

    def test_rehab_center_str_representation(self):
        """Тест строкового представления реабилитационного центра"""
        expected = f'Тестовый центр (Клиника) [ID: {self.rehab_center.id}]'
        self.assertEqual(str(self.rehab_center), expected)

    def test_clinic_active_specialists_method(self):
        """Тест метода active_specialists для клиники"""
        # Создаем активного специалиста
        active_specialist = FacilitySpecialist.objects.create(
            first_name='Активный',
            last_name='Специалист',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=5,
            education='Высшее медицинское',
            is_active=True
        )
        
        # Создаем неактивного специалиста
        inactive_specialist = FacilitySpecialist.objects.create(
            first_name='Неактивный',
            last_name='Специалист',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=3,
            education='Высшее медицинское',
            is_active=False
        )
        
        # Проверяем, что метод возвращает только активных специалистов
        active_specialists = self.clinic.active_specialists()
        self.assertIn(active_specialist, active_specialists)
        self.assertNotIn(inactive_specialist, active_specialists)
        self.assertEqual(active_specialists.count(), 1)
        
        # Проверяем сортировку по фамилии и имени
        self.assertEqual(active_specialists.first(), active_specialist)

    def test_rehab_center_active_specialists_method(self):
        """Тест метода active_specialists для реабилитационного центра"""
        # Создаем активного специалиста
        active_specialist = FacilitySpecialist.objects.create(
            first_name='Активный',
            last_name='Специалист',
            content_type=ContentType.objects.get_for_model(self.rehab_center),
            object_id=self.rehab_center.pk,
            position='Врач',
            experience_years=5,
            education='Высшее медицинское',
            is_active=True
        )
        
        # Создаем неактивного специалиста
        inactive_specialist = FacilitySpecialist.objects.create(
            first_name='Неактивный',
            last_name='Специалист',
            content_type=ContentType.objects.get_for_model(self.rehab_center),
            object_id=self.rehab_center.pk,
            position='Врач',
            experience_years=3,
            education='Высшее медицинское',
            is_active=False
        )
        
        # Проверяем, что метод возвращает только активных специалистов
        active_specialists = self.rehab_center.active_specialists()
        self.assertIn(active_specialist, active_specialists)
        self.assertNotIn(inactive_specialist, active_specialists)
        self.assertEqual(active_specialists.count(), 1)
        
        # Проверяем сортировку по фамилии и имени
        self.assertEqual(active_specialists.first(), active_specialist)

    def test_active_specialists_empty_result(self):
        """Тест метода active_specialists когда нет активных специалистов"""
        # Создаем только неактивного специалиста
        inactive_specialist = FacilitySpecialist.objects.create(
            first_name='Неактивный',
            last_name='Специалист',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=3,
            education='Высшее медицинское',
            is_active=False
        )
        
        # Проверяем, что метод возвращает пустой QuerySet
        active_specialists = self.clinic.active_specialists()
        self.assertEqual(active_specialists.count(), 0)
        self.assertNotIn(inactive_specialist, active_specialists)

    def test_active_specialists_sorting(self):
        """Тест сортировки специалистов по фамилии и имени"""
        # Создаем специалистов в разном порядке
        specialist_b = FacilitySpecialist.objects.create(
            first_name='Борис',
            last_name='Борисов',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=5,
            education='Высшее медицинское',
            is_active=True
        )
        
        specialist_a = FacilitySpecialist.objects.create(
            first_name='Алексей',
            last_name='Алексеев',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=3,
            education='Высшее медицинское',
            is_active=True
        )
        
        specialist_c = FacilitySpecialist.objects.create(
            first_name='Василий',
            last_name='Васильев',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=7,
            education='Высшее медицинское',
            is_active=True
        )
        
        # Проверяем сортировку
        active_specialists = list(self.clinic.active_specialists())
        self.assertEqual(active_specialists[0], specialist_a)  # Алексеев
        self.assertEqual(active_specialists[1], specialist_b)  # Борисов
        self.assertEqual(active_specialists[2], specialist_c)  # Васильев

    def test_active_specialists_cross_facility_isolation(self):
        """Тест изоляции специалистов между разными учреждениями"""
        # Создаем специалиста для клиники
        clinic_specialist = FacilitySpecialist.objects.create(
            first_name='Клинический',
            last_name='Специалист',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=5,
            education='Высшее медицинское',
            is_active=True
        )
        
        # Создаем специалиста для центра
        center_specialist = FacilitySpecialist.objects.create(
            first_name='Центровый',
            last_name='Специалист',
            content_type=ContentType.objects.get_for_model(self.rehab_center),
            object_id=self.rehab_center.pk,
            position='Врач',
            experience_years=3,
            education='Высшее медицинское',
            is_active=True
        )
        
        # Проверяем, что каждый метод возвращает только своих специалистов
        clinic_specialists = self.clinic.active_specialists()
        center_specialists = self.rehab_center.active_specialists()
        
        self.assertIn(clinic_specialist, clinic_specialists)
        self.assertNotIn(center_specialist, clinic_specialists)
        
        self.assertIn(center_specialist, center_specialists)
        self.assertNotIn(clinic_specialist, center_specialists) 
"""
Tests for facilities managers.

This module tests all custom managers in facilities/managers.py.
"""

from django.test import TestCase
from django.db.models import Q
from facilities.models import Clinic, RehabCenter, PrivateDoctor, OrganizationType
from core.models import Region, City
from staff.models import Specialization


class FacilityManagerTest(TestCase):
    """Тесты для базового FacilityManager"""
    
    def setUp(self):
        """Создаем тестовые данные"""
        # Создаем типы организаций
        self.org_type_clinic = OrganizationType.objects.create(
            name="Клиника",
            slug="clinic",
            description="Медицинская клиника"
        )
        self.org_type_rehab = OrganizationType.objects.create(
            name="Реабилитационный центр",
            slug="rehab-center",
            description="Центр реабилитации"
        )
        
        # Создаем регионы и города
        self.region1 = Region.objects.create(
            name="Московская область",
            slug="moscow-region"
        )
        self.region2 = Region.objects.create(
            name="Ленинградская область", 
            slug="leningrad-region"
        )
        
        self.city1 = City.objects.create(
            name="Москва",
            slug="moscow",
            region=self.region1
        )
        self.city2 = City.objects.create(
            name="Санкт-Петербург",
            slug="spb", 
            region=self.region2
        )
        
        # Создаем специализации
        self.spec1 = Specialization.objects.create(
            name="Наркология",
            slug="narcology"
        )
        self.spec2 = Specialization.objects.create(
            name="Психиатрия",
            slug="psychiatry"
        )
        
        # Создаем клиники
        self.clinic1 = Clinic.objects.create(
            name="Клиника 1",
            slug="clinic-1",
            organization_type=self.org_type_clinic,
            city=self.city1,
            description="Описание клиники 1",
            address="Адрес клиники 1",
            is_active=True
        )
        
        self.clinic2 = Clinic.objects.create(
            name="Клиника 2", 
            slug="clinic-2",
            organization_type=self.org_type_clinic,
            city=self.city2,
            description="Описание клиники 2",
            address="Адрес клиники 2",
            is_active=False
        )
        
        # Создаем реабилитационные центры
        self.rehab1 = RehabCenter.objects.create(
            name="Реабилитационный центр 1",
            slug="rehab-1", 
            organization_type=self.org_type_rehab,
            city=self.city1,
            description="Описание центра 1",
            address="Адрес центра 1",
            is_active=True
        )
        
        self.rehab2 = RehabCenter.objects.create(
            name="Реабилитационный центр 2",
            slug="rehab-2",
            organization_type=self.org_type_rehab,
            city=self.city2, 
            description="Описание центра 2",
            address="Адрес центра 2",
            is_active=True
        )
        
        # Создаем частных врачей
        self.doctor1 = PrivateDoctor.objects.create(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            slug="ivanov-ivan",
            organization_type=self.org_type_clinic,
            city=self.city1,
            experience_years=10,
            schedule="Пн-Пт 9:00-18:00",
            is_active=True,
            home_visits=True
        )
        self.doctor1.specializations.add(self.spec1)
        
        self.doctor2 = PrivateDoctor.objects.create(
            first_name="Петр",
            last_name="Петров", 
            middle_name="Петрович",
            slug="petrov-petr",
            organization_type=self.org_type_clinic,
            city=self.city2,
            experience_years=15,
            schedule="Пн-Сб 10:00-19:00",
            is_active=True,
            home_visits=False
        )
        self.doctor2.specializations.add(self.spec2)
        
        self.doctor3 = PrivateDoctor.objects.create(
            first_name="Сергей",
            last_name="Сергеев",
            middle_name="Сергеевич", 
            slug="sergeev-sergey",
            organization_type=self.org_type_clinic,
            city=self.city1,
            experience_years=5,
            schedule="Вт-Чт 14:00-20:00",
            is_active=False,
            home_visits=True
        )
        self.doctor3.specializations.add(self.spec1)
    
    def test_clinic_manager_with_related_data(self):
        """Тест ClinicManager.with_related_data()"""
        clinics = Clinic.objects.with_related_data()
        
        # Проверяем, что возвращается QuerySet
        from django.db.models.query import QuerySet
        self.assertIsInstance(clinics, QuerySet)
        
        # Проверяем, что все клиники включены и отсортированы по имени
        clinic_names = list(clinics.values_list('name', flat=True))
        self.assertEqual(clinic_names, ['Клиника 1', 'Клиника 2'])
        
        # Проверяем, что связанные данные загружены
        clinic = clinics.first()
        self.assertEqual(clinic.city.name, 'Москва')
        self.assertEqual(clinic.city.region.name, 'Московская область')
    
    def test_clinic_manager_with_full_data(self):
        """Тест ClinicManager.with_full_data()"""
        clinics = Clinic.objects.with_full_data()
        
        # Проверяем, что возвращается QuerySet
        from django.db.models.query import QuerySet
        self.assertIsInstance(clinics, QuerySet)
        
        # Проверяем сортировку
        clinic_names = list(clinics.values_list('name', flat=True))
        self.assertEqual(clinic_names, ['Клиника 1', 'Клиника 2'])
    
    def test_rehab_center_manager_with_related_data(self):
        """Тест RehabCenterManager.with_related_data()"""
        rehabs = RehabCenter.objects.with_related_data()
        
        # Проверяем, что возвращается QuerySet
        from django.db.models.query import QuerySet
        self.assertIsInstance(rehabs, QuerySet)
        
        # Проверяем сортировку
        rehab_names = list(rehabs.values_list('name', flat=True))
        self.assertEqual(rehab_names, ['Реабилитационный центр 1', 'Реабилитационный центр 2'])
    
    def test_rehab_center_manager_with_full_data(self):
        """Тест RehabCenterManager.with_full_data()"""
        rehabs = RehabCenter.objects.with_full_data()
        
        # Проверяем, что возвращается QuerySet
        from django.db.models.query import QuerySet
        self.assertIsInstance(rehabs, QuerySet)
        
        # Проверяем сортировку
        rehab_names = list(rehabs.values_list('name', flat=True))
        self.assertEqual(rehab_names, ['Реабилитационный центр 1', 'Реабилитационный центр 2'])
    
    def test_private_doctor_manager_with_related_data(self):
        """Тест PrivateDoctorManager.with_related_data()"""
        doctors = PrivateDoctor.objects.with_related_data()
        
        # Проверяем, что возвращается QuerySet
        from django.db.models.query import QuerySet
        self.assertIsInstance(doctors, QuerySet)
        
        # Проверяем, что только активные врачи включены и отсортированы
        doctor_names = list(doctors.values_list('last_name', flat=True))
        self.assertEqual(doctor_names, ['Иванов', 'Петров'])
        
        # Проверяем, что связанные данные загружены
        doctor = doctors.first()
        self.assertEqual(doctor.city.name, 'Москва')
        self.assertEqual(doctor.city.region.name, 'Московская область')
    
    def test_private_doctor_manager_with_full_data(self):
        """Тест PrivateDoctorManager.with_full_data()"""
        doctors = PrivateDoctor.objects.with_full_data()
        
        # Проверяем, что возвращается QuerySet
        from django.db.models.query import QuerySet
        self.assertIsInstance(doctors, QuerySet)
        
        # Проверяем, что только активные врачи включены и отсортированы
        doctor_names = list(doctors.values_list('last_name', flat=True))
        self.assertEqual(doctor_names, ['Иванов', 'Петров'])
    
    def test_private_doctor_manager_by_specialization_object(self):
        """Тест PrivateDoctorManager.by_specialization() с объектом"""
        doctors = PrivateDoctor.objects.by_specialization(self.spec1)
        
        # Проверяем, что возвращается врач с нужной специализацией
        self.assertEqual(doctors.count(), 2)  # Иванов и Сергеев имеют spec1
        doctor_names = list(doctors.values_list('last_name', flat=True))
        self.assertIn('Иванов', doctor_names)
        self.assertIn('Сергеев', doctor_names)
    
    def test_private_doctor_manager_by_specialization_slug(self):
        """Тест PrivateDoctorManager.by_specialization() со slug"""
        doctors = PrivateDoctor.objects.by_specialization('psychiatry')
        
        # Проверяем, что возвращается врач с нужной специализацией
        self.assertEqual(doctors.count(), 1)
        self.assertEqual(doctors.first().last_name, 'Петров')
    
    def test_private_doctor_manager_with_home_visits(self):
        """Тест PrivateDoctorManager.with_home_visits()"""
        doctors = PrivateDoctor.objects.with_home_visits()
        
        # Проверяем, что возвращаются врачи с выездом на дом
        self.assertEqual(doctors.count(), 2)  # Иванов и Сергеев
        doctor_names = list(doctors.values_list('last_name', flat=True))
        self.assertIn('Иванов', doctor_names)
        self.assertIn('Сергеев', doctor_names)
    
    def test_private_doctor_manager_search_by_name(self):
        """Тест PrivateDoctorManager.search() по имени"""
        doctors = PrivateDoctor.objects.search('Иван')
        
        # Проверяем, что возвращается врач с именем Иван
        self.assertEqual(doctors.count(), 1)
        self.assertEqual(doctors.first().first_name, 'Иван')
    
    def test_private_doctor_manager_search_by_last_name(self):
        """Тест PrivateDoctorManager.search() по фамилии"""
        doctors = PrivateDoctor.objects.search('Петров')
        
        # Проверяем, что возвращается врач с фамилией Петров
        self.assertEqual(doctors.count(), 1)
        self.assertEqual(doctors.first().last_name, 'Петров')
    
    def test_private_doctor_manager_search_by_specialization(self):
        """Тест PrivateDoctorManager.search() по специализации"""
        doctors = PrivateDoctor.objects.search('Наркология')
        
        # Проверяем, что возвращаются врачи с нужной специализацией
        self.assertEqual(doctors.count(), 2)  # Иванов и Сергеев
        doctor_names = list(doctors.values_list('last_name', flat=True))
        self.assertIn('Иванов', doctor_names)
        self.assertIn('Сергеев', doctor_names)
    
    def test_private_doctor_manager_search_by_city(self):
        """Тест PrivateDoctorManager.search() по городу"""
        doctors = PrivateDoctor.objects.search('Москва')
        
        # Проверяем, что возвращаются врачи из Москвы
        self.assertEqual(doctors.count(), 2)  # Иванов и Сергеев
        doctor_names = list(doctors.values_list('last_name', flat=True))
        self.assertIn('Иванов', doctor_names)
        self.assertIn('Сергеев', doctor_names)
    
    def test_private_doctor_manager_search_empty_query(self):
        """Тест PrivateDoctorManager.search() с пустым запросом"""
        doctors = PrivateDoctor.objects.search('')
        
        # Проверяем, что возвращается пустой QuerySet
        self.assertEqual(doctors.count(), 0)
    
    def test_private_doctor_manager_search_none_query(self):
        """Тест PrivateDoctorManager.search() с None"""
        doctors = PrivateDoctor.objects.search(None)
        
        # Проверяем, что возвращается пустой QuerySet
        self.assertEqual(doctors.count(), 0)
    
    def test_private_doctor_manager_search_no_results(self):
        """Тест PrivateDoctorManager.search() без результатов"""
        doctors = PrivateDoctor.objects.search('Несуществующий врач')
        
        # Проверяем, что возвращается пустой QuerySet
        self.assertEqual(doctors.count(), 0)
    
    def test_clinic_manager_by_region_object(self):
        """Тест FacilityManager.by_region() с объектом"""
        clinics = Clinic.objects.by_region(self.region1)
        
        # Проверяем, что возвращается только клиника из нужного региона
        self.assertEqual(clinics.count(), 1)
        self.assertEqual(clinics.first().name, 'Клиника 1')
    
    def test_clinic_manager_by_region_slug(self):
        """Тест FacilityManager.by_region() со slug"""
        clinics = Clinic.objects.by_region('leningrad-region')
        
        # Проверяем, что возвращается только клиника из нужного региона
        self.assertEqual(clinics.count(), 1)
        self.assertEqual(clinics.first().name, 'Клиника 2')
    
    def test_clinic_manager_by_city_object(self):
        """Тест FacilityManager.by_city() с объектом"""
        clinics = Clinic.objects.by_city(self.city1)
        
        # Проверяем, что возвращается только клиника из нужного города
        self.assertEqual(clinics.count(), 1)
        self.assertEqual(clinics.first().name, 'Клиника 1')
    
    def test_clinic_manager_by_city_slug(self):
        """Тест FacilityManager.by_city() со slug"""
        clinics = Clinic.objects.by_city('spb')
        
        # Проверяем, что возвращается только клиника из нужного города
        self.assertEqual(clinics.count(), 1)
        self.assertEqual(clinics.first().name, 'Клиника 2')
    
    def test_clinic_manager_search_by_name(self):
        """Тест FacilityManager.search() по названию"""
        clinics = Clinic.objects.search('Клиника 1')
        
        # Проверяем, что возвращается нужная клиника
        self.assertEqual(clinics.count(), 1)
        self.assertEqual(clinics.first().name, 'Клиника 1')
    
    def test_clinic_manager_search_by_description(self):
        """Тест FacilityManager.search() по описанию"""
        clinics = Clinic.objects.search('Описание клиники 2')
        
        # Проверяем, что возвращается нужная клиника
        self.assertEqual(clinics.count(), 1)
        self.assertEqual(clinics.first().name, 'Клиника 2')
    
    def test_clinic_manager_search_by_address(self):
        """Тест FacilityManager.search() по адресу"""
        clinics = Clinic.objects.search('Адрес клиники 1')
        
        # Проверяем, что возвращается нужная клиника
        self.assertEqual(clinics.count(), 1)
        self.assertEqual(clinics.first().name, 'Клиника 1')
    
    def test_clinic_manager_search_empty_query(self):
        """Тест FacilityManager.search() с пустым запросом"""
        clinics = Clinic.objects.search('')
        
        # Проверяем, что возвращается пустой QuerySet
        self.assertEqual(clinics.count(), 0)
    
    def test_clinic_manager_search_none_query(self):
        """Тест FacilityManager.search() с None"""
        clinics = Clinic.objects.search(None)
        
        # Проверяем, что возвращается пустой QuerySet
        self.assertEqual(clinics.count(), 0)
    
    def test_clinic_manager_search_no_results(self):
        """Тест FacilityManager.search() без результатов"""
        clinics = Clinic.objects.search('Несуществующая клиника')
        
        # Проверяем, что возвращается пустой QuerySet
        self.assertEqual(clinics.count(), 0)
    
    def test_clinic_manager_active(self):
        """Тест FacilityManager.active()"""
        active_clinics = Clinic.objects.active()
        
        # Проверяем, что возвращается только активная клиника
        self.assertEqual(active_clinics.count(), 1)
        self.assertEqual(active_clinics.first().name, 'Клиника 1')
    
    def test_rehab_center_manager_active(self):
        """Тест FacilityManager.active() для реабилитационных центров"""
        active_rehabs = RehabCenter.objects.active()
        
        # Проверяем, что возвращаются только активные центры
        self.assertEqual(active_rehabs.count(), 2)
        rehab_names = list(active_rehabs.values_list('name', flat=True))
        self.assertIn('Реабилитационный центр 1', rehab_names)
        self.assertIn('Реабилитационный центр 2', rehab_names) 
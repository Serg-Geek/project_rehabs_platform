from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.files.storage import default_storage
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.conf import settings
import time

from staff.models import MedicalSpecialist, FacilitySpecialist, SpecialistDocument, Specialization
from staff.admin import FacilitySpecialistForm, SpecialistDocumentForm
from facilities.models import Clinic, OrganizationType
from core.models import City, Region

User = get_user_model()

class StaffModelsTest(TestCase):
    def setUp(self):
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
        
        self.medical_specialist = MedicalSpecialist.objects.create(
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович',
            slug='ivanov-ivan',
            is_active=True,
            experience_years=5,
            education='Высшее медицинское'
        )
        self.medical_specialist.specializations.add(self.specialization)
        
        # Создаем тестовый файл
        self.test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        # Создаем документ специалиста
        self.document = SpecialistDocument.objects.create(
            specialist=self.medical_specialist,
            document_type='diploma',
            title='Диплом о высшем образовании',
            document=self.test_file,
            number='123456',
            issue_date=date(2020, 1, 1),
            expiry_date=date(2025, 1, 1),
            is_active=True
        )
        
        # Создаем FacilitySpecialist
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

    def test_medical_specialist_creation(self):
        """Тест создания MedicalSpecialist"""
        self.assertEqual(self.medical_specialist.get_full_name(), 'Иванов Иван Иванович')
        self.assertTrue(self.medical_specialist.is_active)
        self.assertEqual(self.medical_specialist.specializations.count(), 1)
        self.assertEqual(self.medical_specialist.specializations.first().name, 'Терапевт')

    def test_facility_specialist_creation(self):
        """Тест создания FacilitySpecialist"""
        self.assertEqual(self.facility_specialist.get_full_name(), 'Петров Петр Петрович')
        self.assertTrue(self.facility_specialist.is_active)
        self.assertEqual(self.facility_specialist.position, 'Главный врач')
        self.assertEqual(self.facility_specialist.specializations.count(), 1)
        self.assertEqual(self.facility_specialist.facility, self.clinic)

    def test_specialist_document_creation(self):
        """Тест создания SpecialistDocument"""
        self.assertEqual(self.document.specialist, self.medical_specialist)
        self.assertEqual(self.document.document_type, 'diploma')
        self.assertEqual(self.document.title, 'Диплом о высшем образовании')
        self.assertEqual(self.document.number, '123456')
        self.assertEqual(self.document.issue_date, date(2020, 1, 1))
        self.assertEqual(self.document.expiry_date, date(2025, 1, 1))
        self.assertTrue(self.document.is_active)
        self.assertTrue(self.document.document)

    def test_specialization_creation(self):
        """Тест создания Specialization"""
        # Отладочная информация
        print("\nВсего MedicalSpecialist:", MedicalSpecialist.objects.count())
        print("Все MedicalSpecialist:", list(MedicalSpecialist.objects.values_list('id', 'first_name', 'last_name')))
        print("MedicalSpecialist в специализации:", list(self.specialization.medicalspecialist_set.values_list('id', 'first_name', 'last_name')))
        
        self.assertEqual(self.specialization.name, 'Терапевт')
        self.assertEqual(self.specialization.description, 'Врач общей практики')
        
        # Проверяем, что у специализации есть 2 специалиста
        self.assertEqual(self.specialization.medicalspecialist_set.count(), 2)
        
        # Проверяем, что MedicalSpecialist в списке
        self.assertIn(self.medical_specialist, self.specialization.medicalspecialist_set.all())
        
        # Проверяем, что FacilitySpecialist в списке через его базовый класс
        self.assertIn(self.facility_specialist.medicalspecialist_ptr, self.specialization.medicalspecialist_set.all())
        
        # Проверяем, что FacilitySpecialist правильно связан с клиникой
        self.assertEqual(self.facility_specialist.facility, self.clinic)

    def tearDown(self):
        """Очистка после тестов"""
        # Удаляем тестовые файлы
        if self.document.document:
            if default_storage.exists(self.document.document.name):
                default_storage.delete(self.document.document.name)
        super().tearDown()

class StaffFormsTest(TestCase):
    def setUp(self):
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

    def test_facility_specialist_form(self):
        """Тест формы FacilitySpecialistForm"""
        clinic_type = ContentType.objects.get_for_model(Clinic)
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'middle_name': 'Иванович',
            'facility_type': clinic_type.id,
            'facility_id': self.clinic.id,
            'position': 'Врач',
            'experience_years': 5,
            'education': 'Высшее медицинское',
            'specializations': [self.specialization.id]
        }
        form = FacilitySpecialistForm(data=form_data)
        
        # Проверяем ошибки формы
        if not form.is_valid():
            print("\nОшибки формы:", form.errors)
        
        self.assertTrue(form.is_valid())
        
        # Проверяем создание объекта
        specialist = form.save()
        self.assertEqual(specialist.get_full_name(), 'Иванов Иван Иванович')
        self.assertEqual(specialist.position, 'Врач')
        self.assertEqual(specialist.facility, self.clinic)
        self.assertEqual(specialist.experience_years, 5)
        self.assertEqual(specialist.education, 'Высшее медицинское')
        self.assertEqual(specialist.specializations.count(), 1)
        self.assertEqual(specialist.specializations.first(), self.specialization)

    def test_specialist_document_form(self):
        """Тест формы SpecialistDocumentForm"""
        # Создаем тестовый файл
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        form_data = {
            'specialist': self.facility_specialist.id,
            'document_type': 'diploma',
            'title': 'Диплом о высшем образовании',
            'document': test_file,
            'number': '123456',
            'issue_date': date(2020, 1, 1),
            'expiry_date': date(2025, 1, 1),
            'is_active': True
        }
        
        form = SpecialistDocumentForm(data=form_data, files={'document': test_file})
        
        # Проверяем ошибки формы
        if not form.is_valid():
            print("\nОшибки формы:", form.errors)
        
        self.assertTrue(form.is_valid())
        
        # Проверяем создание объекта
        document = form.save()
        # Проверяем, что документ связан с базовым классом MedicalSpecialist
        self.assertEqual(document.specialist, self.facility_specialist.medicalspecialist_ptr)
        self.assertEqual(document.document_type, 'diploma')
        self.assertEqual(document.title, 'Диплом о высшем образовании')
        self.assertEqual(document.number, '123456')
        self.assertEqual(document.issue_date, date(2020, 1, 1))
        self.assertEqual(document.expiry_date, date(2025, 1, 1))
        self.assertTrue(document.is_active)
        self.assertTrue(document.document)
        
        # Очищаем тестовый файл
        if document.document:
            if default_storage.exists(document.document.name):
                default_storage.delete(document.document.name)

class StaffViewsTest(TestCase):
    pass

class StaffAdminTest(TestCase):
    pass

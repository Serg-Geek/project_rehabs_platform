from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from datetime import date

from staff.admin import FacilitySpecialistForm, SpecialistDocumentForm
from staff.models import MedicalSpecialist, FacilitySpecialist, Specialization
from facilities.models import Clinic, OrganizationType
from core.models import City, Region


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

    def test_facility_specialist_form_validation_errors(self):
        """Тест валидации формы FacilitySpecialistForm с ошибками"""
        # Форма без обязательных полей
        form_data = {
            'first_name': '',  # Пустое обязательное поле
            'last_name': 'Иванов',
            'position': 'Врач'
        }
        form = FacilitySpecialistForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_specialist_document_form_validation_errors(self):
        """Тест валидации формы SpecialistDocumentForm с ошибками"""
        # Форма без обязательных полей
        form_data = {
            'specialist': self.facility_specialist.id,
            'document_type': '',  # Пустое обязательное поле
            'title': 'Диплом'
        }
        form = SpecialistDocumentForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn('document_type', form.errors)

    def test_facility_specialist_form_fields(self):
        """Тест полей формы FacilitySpecialistForm"""
        form = FacilitySpecialistForm()
        
        # Проверяем наличие основных полей
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('middle_name', form.fields)
        self.assertIn('facility_type', form.fields)
        self.assertIn('facility_id', form.fields)
        self.assertIn('position', form.fields)
        self.assertIn('experience_years', form.fields)
        self.assertIn('education', form.fields)
        self.assertIn('specializations', form.fields)

    def test_specialist_document_form_fields(self):
        """Тест полей формы SpecialistDocumentForm"""
        form = SpecialistDocumentForm()
        
        # Проверяем наличие основных полей
        self.assertIn('specialist', form.fields)
        self.assertIn('document_type', form.fields)
        self.assertIn('title', form.fields)
        self.assertIn('document', form.fields)
        self.assertIn('number', form.fields)
        self.assertIn('issue_date', form.fields)
        self.assertIn('expiry_date', form.fields)
        self.assertIn('is_active', form.fields) 
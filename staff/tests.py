from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from .models import (
    Specialization,
    MedicalSpecialist,
    FacilitySpecialist,
    SpecialistDocument
)
from facilities.models import Clinic, RehabCenter, OrganizationType
from core.models import City, Region

class StaffModelsTest(TestCase):
    """Тесты для моделей приложения staff"""

    def setUp(self):
        """Создание тестовых данных"""
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

        # Создаем типы организаций
        self.clinic_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic',
            description='Медицинская клиника',
            competencies='Лечение пациентов'
        )
        self.rehab_type = OrganizationType.objects.create(
            name='Реабилитационный центр',
            slug='rehab',
            description='Реабилитационный центр',
            competencies='Реабилитация пациентов'
        )

        # Создаем специализации
        self.specialization1 = Specialization.objects.create(
            name='Психиатр',
            description='Описание специализации'
        )
        self.specialization2 = Specialization.objects.create(
            name='Психолог',
            description='Описание специализации'
        )

        # Создаем клинику
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника',
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            organization_type=self.clinic_type
        )

        # Создаем реабилитационный центр
        self.rehab_center = RehabCenter.objects.create(
            name='Тестовый центр',
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-98',
            email='rehab@test.com',
            organization_type=self.rehab_type
        )

    def test_specialization_creation(self):
        """Тест создания специализации"""
        specialization = Specialization.objects.create(
            name='Новая специализация',
            description='Описание новой специализации'
        )
        self.assertEqual(specialization.name, 'Новая специализация')
        self.assertTrue(specialization.slug)
        self.assertEqual(specialization.description, 'Описание новой специализации')

    def test_specialization_slug_generation(self):
        """Тест автоматического формирования slug для специализации"""
        specialization = Specialization.objects.create(
            name='Тестовая специализация',
            description='Описание'
        )
        self.assertEqual(specialization.slug, 'testovaya-spetsializatsiya')

    def test_medical_specialist_creation(self):
        """Тест создания медицинского специалиста"""
        specialist = MedicalSpecialist.objects.create(
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович',
            experience_years=5,
            education='Высшее медицинское'
        )
        specialist.specializations.add(self.specialization1)
        
        self.assertEqual(specialist.first_name, 'Иван')
        self.assertEqual(specialist.last_name, 'Иванов')
        self.assertEqual(specialist.middle_name, 'Иванович')
        self.assertEqual(specialist.experience_years, 5)
        self.assertEqual(specialist.education, 'Высшее медицинское')
        self.assertEqual(specialist.specializations.count(), 1)

    def test_medical_specialist_full_name(self):
        """Тест метода get_full_name для медицинского специалиста"""
        specialist = MedicalSpecialist.objects.create(
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович',
            experience_years=5,
            education='Высшее медицинское'
        )
        self.assertEqual(
            specialist.get_full_name(),
            'Иванов Иван Иванович'
        )

        specialist_no_middle = MedicalSpecialist.objects.create(
            first_name='Петр',
            last_name='Петров',
            experience_years=3,
            education='Высшее медицинское'
        )
        self.assertEqual(
            specialist_no_middle.get_full_name(),
            'Петров Петр'
        )

    def test_facility_specialist_creation(self):
        """Тест создания специалиста учреждения"""
        specialist = FacilitySpecialist.objects.create(
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович',
            experience_years=5,
            education='Высшее медицинское',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.id,
            position='Главный врач'
        )
        specialist.specializations.add(self.specialization1)
        
        self.assertEqual(specialist.facility, self.clinic)
        self.assertEqual(specialist.position, 'Главный врач')
        self.assertEqual(specialist.specializations.count(), 1)

    def test_specialist_document_creation(self):
        """Тест создания документа специалиста"""
        specialist = MedicalSpecialist.objects.create(
            first_name='Иван',
            last_name='Иванов',
            experience_years=5,
            education='Высшее медицинское'
        )

        document = SpecialistDocument.objects.create(
            specialist=specialist,
            document_type='diploma',
            title='Диплом о высшем образовании',
            number='123456',
            issue_date='2020-01-01'
        )

        self.assertEqual(document.specialist, specialist)
        self.assertEqual(document.document_type, 'diploma')
        self.assertEqual(document.title, 'Диплом о высшем образовании')
        self.assertEqual(document.number, '123456')
        self.assertEqual(str(document.issue_date), '2020-01-01')

    def test_facility_specialist_validation(self):
        """Тест валидации специалиста учреждения"""
        # Попытка создать специалиста без привязки к учреждению
        specialist = FacilitySpecialist(
            first_name='Иван',
            last_name='Иванов',
            experience_years=5,
            education='Высшее медицинское'
        )
        with self.assertRaises(ValueError):  # Более конкретное исключение
            specialist.save()

    def test_specialist_document_validation(self):
        """Тест валидации документа специалиста"""
        specialist = MedicalSpecialist.objects.create(
            first_name='Иван',
            last_name='Иванов',
            experience_years=5,
            education='Высшее медицинское'
        )

        # Попытка создать документ без обязательных полей
        document = SpecialistDocument(
            specialist=specialist,
            document_type='diploma'
        )
        with self.assertRaises(Exception):
            document.save()

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from facilities.models import Clinic, RehabCenter, PrivateDoctor, FacilityImage, OrganizationType
from staff.models import Specialization, FacilitySpecialist
from core.models import Region, City


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
        """Тест сортировки специалистов по order и id"""
        # Создаем специалистов в разном порядке
        specialist_b = FacilitySpecialist.objects.create(
            first_name='Борис',
            last_name='Борисов',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=5,
            education='Высшее медицинское',
            is_active=True,
            order=3  # Высокий порядок
        )
        
        specialist_a = FacilitySpecialist.objects.create(
            first_name='Алексей',
            last_name='Алексеев',
            content_type=ContentType.objects.get_for_model(self.clinic),
            object_id=self.clinic.pk,
            position='Врач',
            experience_years=3,
            education='Высшее медицинское',
            is_active=True,
            order=1  # Низкий порядок - должен быть первым
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
            # Без order - должен быть после тех, у кого есть order
        )
        
        # Проверяем сортировку
        active_specialists = list(self.clinic.active_specialists())
        self.assertEqual(active_specialists[0], specialist_a)  # Алексеев (order=1)
        self.assertEqual(active_specialists[1], specialist_b)  # Борисов (order=3)
        self.assertEqual(active_specialists[2], specialist_c)  # Васильев (без order)

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


class MainImageTest(TestCase):
    """Тесты для проверки логики главного фото"""
    
    def setUp(self):
        # Создаем необходимые объекты
        self.region = Region.objects.create(name='Тестовый регион')
        self.city = City.objects.create(name='Тестовый город', region=self.region)
        self.org_type = OrganizationType.objects.create(
            name='Тестовая организация',
            slug='test-org',
            description='Описание'
        )
        
        # Создаем клинику
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            organization_type=self.org_type,
            city=self.city,
            description='Описание клиники',
            address='Тестовый адрес',
            phone='+7-999-999-99-99'
        )
        
        # Создаем реабилитационный центр
        self.rehab = RehabCenter.objects.create(
            name='Тестовый реабилитационный центр',
            slug='test-rehab',
            organization_type=self.org_type,
            city=self.city,
            description='Описание центра',
            address='Тестовый адрес',
            phone='+7-999-999-99-99'
        )
        
        # Создаем специализацию для врача
        self.specialization = Specialization.objects.create(
            name='Тестовая специализация',
            description='Описание специализации'
        )
        
        # Создаем частного врача
        self.doctor = PrivateDoctor.objects.create(
            first_name='Иван',
            last_name='Иванов',
            organization_type=self.org_type,
            city=self.city,
            description='Описание врача',
            address='Тестовый адрес',
            phone='+7-999-999-99-99',
            experience_years=10,
            schedule='Пн-Пт 9:00-18:00'
        )
        self.doctor.specializations.add(self.specialization)

    def test_main_image_property(self):
        """Тест свойства main_image для всех типов учреждений"""
        # Создаем изображения для клиники
        image1 = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='test1.jpg',
            title='Первое изображение'
        )
        image2 = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='test2.jpg',
            title='Второе изображение',
            is_main=True
        )
        
        # Проверяем, что main_image возвращает изображение с is_main=True
        self.assertEqual(self.clinic.main_image, image2)
        
        # Убираем флаг is_main у второго изображения
        image2.is_main = False
        image2.save()
        
        # Проверяем, что main_image возвращает первое изображение
        self.assertEqual(self.clinic.main_image, image1)

    def test_single_main_image_signal(self):
        """Тест сигнала для обеспечения единственного главного изображения"""
        # Создаем несколько изображений для клиники
        image1 = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='test1.jpg',
            title='Первое изображение',
            is_main=True
        )
        image2 = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='test2.jpg',
            title='Второе изображение',
            is_main=True
        )
        
        # Проверяем, что только второе изображение осталось главным
        image1.refresh_from_db()
        image2.refresh_from_db()
        
        self.assertFalse(image1.is_main)
        self.assertTrue(image2.is_main)

    def test_main_image_for_rehab_center(self):
        """Тест main_image для реабилитационного центра"""
        image = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(RehabCenter),
            object_id=self.rehab.id,
            image='test.jpg',
            title='Изображение центра',
            is_main=True
        )
        
        self.assertEqual(self.rehab.main_image, image)

    def test_main_image_for_private_doctor(self):
        """Тест main_image для частного врача"""
        image = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(PrivateDoctor),
            object_id=self.doctor.id,
            image='test.jpg',
            title='Фото врача',
            is_main=True
        )
        
        self.assertEqual(self.doctor.main_image, image)

    def test_no_images_returns_none(self):
        """Тест, что main_image возвращает None если нет изображений"""
        self.assertIsNone(self.clinic.main_image)
        self.assertIsNone(self.rehab.main_image)
        self.assertIsNone(self.doctor.main_image)

    def test_inactive_images_not_included(self):
        """Тест, что неактивные изображения не включаются в main_image"""
        # Создаем активное изображение
        active_image = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='active.jpg',
            title='Активное изображение',
            is_active=True
        )
        
        # Создаем неактивное изображение
        inactive_image = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='inactive.jpg',
            title='Неактивное изображение',
            is_active=False
        )
        
        # Проверяем, что main_image возвращает только активное изображение
        self.assertEqual(self.clinic.main_image, active_image)
        
        # Делаем активное изображение неактивным
        active_image.is_active = False
        active_image.save()
        
        # Проверяем, что main_image возвращает None
        self.assertIsNone(self.clinic.main_image)

    def test_main_image_prioritizes_active_main_image(self):
        """Тест, что main_image приоритизирует активное главное изображение"""
        # Создаем неактивное главное изображение
        inactive_main = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='inactive_main.jpg',
            title='Неактивное главное',
            is_main=True,
            is_active=False
        )
        
        # Создаем активное обычное изображение
        active_regular = FacilityImage.objects.create(
            content_type=ContentType.objects.get_for_model(Clinic),
            object_id=self.clinic.id,
            image='active_regular.jpg',
            title='Активное обычное',
            is_active=True
        )
        
        # Проверяем, что main_image возвращает активное обычное изображение
        self.assertEqual(self.clinic.main_image, active_regular)
        
        # Делаем главное изображение активным
        inactive_main.is_active = True
        inactive_main.save()
        
        # Проверяем, что main_image возвращает активное главное изображение
        self.assertEqual(self.clinic.main_image, inactive_main) 
"""
Тесты для моделей медицинских учреждений.

Этот модуль содержит тесты для проверки функциональности моделей:
- MedicalFacility (базовая модель учреждения)
- Review (модель отзывов)
- OrganizationType (типы организаций)
- City (города)
- Region (регионы)
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from facilities.models import MedicalFacility, OrganizationType, City, Review, FacilityImage
from core.models import Region

class MedicalFacilityModelTest(TestCase):
    """
    Тесты для модели MedicalFacility.
    
    Проверяет:
    1. Создание медицинского учреждения
    2. Работу с изображениями
    3. Строковое представление
    4. Генерацию URL
    """
    
    def setUp(self):
        """
        Подготовка тестовых данных.
        
        Создает:
        - Регион и город
        - Тип организации
        - Тестовое изображение
        """
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
        self.org_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic',
            description='Описание клиники',
            competencies='Компетенции клиники'
        )
        
        # Создаем тестовое изображение
        image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        self.image = SimpleUploadedFile(
            'test_image.gif',
            image_content,
            content_type='image/gif'
        )

    def test_facility_creation(self):
        """
        Тест создания медицинского учреждения.
        
        Проверяет:
        - Корректное сохранение всех полей
        - Значения по умолчанию
        - Связи с другими моделями
        - Обязательные поля
        """
        facility = MedicalFacility.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            organization_type=self.org_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            website='http://test.com',
            license_number='123456',
            description='Тестовое описание'
        )
        
        self.assertEqual(facility.name, 'Тестовая клиника')
        self.assertEqual(facility.slug, 'test-clinic')
        self.assertEqual(facility.organization_type, self.org_type)
        self.assertEqual(facility.city, self.city)
        self.assertEqual(facility.address, 'Тестовый адрес')
        self.assertEqual(facility.phone, '+7 (999) 999-99-99')
        self.assertEqual(facility.email, 'test@test.com')
        self.assertEqual(facility.website, 'http://test.com')
        self.assertEqual(facility.license_number, '123456')
        self.assertEqual(facility.description, 'Тестовое описание')
        self.assertTrue(facility.is_active)

    def test_facility_with_image(self):
        """
        Тест создания учреждения с изображением.
        
        Проверяет:
        - Корректное сохранение изображения
        - Связь изображения с учреждением
        - Формат имени файла
        - Метаданные изображения
        """
        facility = MedicalFacility.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            organization_type=self.org_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            license_number='123456'
        )
        
        facility_image = FacilityImage.objects.create(
            facility=facility,
            image=self.image,
            image_type=FacilityImage.ImageType.MAIN,
            title='Главное фото',
            is_main=True
        )
        
        self.assertTrue(facility.images.exists())
        image = facility.images.first()
        self.assertTrue(image.image.name.startswith('facilities/test_image'))
        self.assertTrue(image.image.name.endswith('.gif'))
        self.assertEqual(image.title, 'Главное фото')
        self.assertTrue(image.is_main)

    def test_facility_str(self):
        """
        Тест строкового представления учреждения.
        
        Проверяет:
        - Формат строки
        - Включение названия и типа организации
        """
        facility = MedicalFacility.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            organization_type=self.org_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            license_number='123456'
        )
        
        self.assertEqual(str(facility), 'Тестовая клиника (Клиника)')

    def test_facility_absolute_url(self):
        """
        Тест генерации URL учреждения.
        
        Проверяет:
        - Корректный формат URL
        - Использование slug в URL
        """
        facility = MedicalFacility.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            organization_type=self.org_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            license_number='123456'
        )
        
        self.assertEqual(facility.get_absolute_url(), f'/facilities/{facility.slug}/')

class ReviewModelTest(TestCase):
    """
    Тесты для модели Review.
    
    Проверяет:
    1. Создание отзывов
    2. Связи с учреждениями
    3. Строковое представление
    """
    
    def setUp(self):
        """
        Подготовка тестовых данных.
        
        Создает:
        - Регион и город
        - Тип организации
        - Тестовое учреждение
        """
        self.region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region'
        )
        self.city = City.objects.create(
            name='Тестовый город',
            slug='test-city',
            region=self.region
        )
        self.org_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic',
            description='Описание клиники',
            competencies='Компетенции клиники'
        )
        self.facility = MedicalFacility.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            organization_type=self.org_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            license_number='123456'
        )

    def test_review_creation(self):
        """
        Тест создания отзыва.
        
        Проверяет:
        - Корректное сохранение всех полей
        - Связь с учреждением
        - Автоматическое заполнение даты
        """
        review = Review.objects.create(
            facility=self.facility,
            rating=5,
            content='Тестовый отзыв'
        )
        
        self.assertEqual(review.facility, self.facility)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, 'Тестовый отзыв')
        self.assertIsNotNone(review.created_at)

    def test_review_str(self):
        """
        Тест строкового представления отзыва.
        
        Проверяет:
        - Формат строки
        - Включение названия учреждения и рейтинга
        """
        review = Review.objects.create(
            facility=self.facility,
            rating=5,
            content='Тестовый отзыв'
        )
        
        self.assertEqual(str(review), f'Отзыв о {self.facility.name} (5 звезд)')

class OrganizationTypeModelTest(TestCase):
    """
    Тесты для модели OrganizationType.
    
    Проверяет:
    1. Создание типов организаций
    2. Строковое представление
    """
    
    def test_org_type_creation(self):
        """
        Тест создания типа организации.
        
        Проверяет:
        - Корректное сохранение всех полей
        - Обязательные поля
        - Описание и компетенции
        """
        org_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic',
            description='Описание клиники',
            competencies='Компетенции клиники'
        )
        
        self.assertEqual(org_type.name, 'Клиника')
        self.assertEqual(org_type.slug, 'clinic')
        self.assertEqual(org_type.description, 'Описание клиники')
        self.assertEqual(org_type.competencies, 'Компетенции клиники')

    def test_org_type_str(self):
        """
        Тест строкового представления типа организации.
        
        Проверяет:
        - Формат строки
        - Отображение названия
        """
        org_type = OrganizationType.objects.create(
            name='Клиника',
            slug='clinic',
            description='Описание клиники',
            competencies='Компетенции клиники'
        )
        
        self.assertEqual(str(org_type), 'Клиника')

class CityModelTest(TestCase):
    """
    Тесты для модели City.
    
    Проверяет:
    1. Создание городов
    2. Связи с регионами
    3. Строковое представление
    """
    
    def setUp(self):
        """
        Подготовка тестовых данных.
        
        Создает:
        - Тестовый регион
        """
        self.region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region'
        )

    def test_city_creation(self):
        """
        Тест создания города.
        
        Проверяет:
        - Корректное сохранение всех полей
        - Связь с регионом
        - Обязательные поля
        """
        city = City.objects.create(
            name='Тестовый город',
            slug='test-city',
            region=self.region
        )
        
        self.assertEqual(city.name, 'Тестовый город')
        self.assertEqual(city.slug, 'test-city')
        self.assertEqual(city.region, self.region)

    def test_city_str(self):
        """
        Тест строкового представления города.
        
        Проверяет:
        - Формат строки
        - Включение названия города и региона
        """
        city = City.objects.create(
            name='Тестовый город',
            slug='test-city',
            region=self.region
        )
        
        self.assertEqual(str(city), f'{city.name}, {city.region.name}')

class RegionModelTest(TestCase):
    """
    Тесты для модели Region.
    
    Проверяет:
    1. Создание регионов
    2. Строковое представление
    """
    
    def test_region_creation(self):
        """
        Тест создания региона.
        
        Проверяет:
        - Корректное сохранение всех полей
        - Обязательные поля
        """
        region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region'
        )
        
        self.assertEqual(region.name, 'Тестовый регион')
        self.assertEqual(region.slug, 'test-region')

    def test_region_str(self):
        """
        Тест строкового представления региона.
        
        Проверяет:
        - Формат строки
        - Отображение названия
        """
        region = Region.objects.create(
            name='Тестовый регион',
            slug='test-region'
        )
        
        self.assertEqual(str(region), 'Тестовый регион') 
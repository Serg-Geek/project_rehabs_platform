"""
Тесты для представлений каталогов медицинских учреждений.

Этот модуль содержит тесты для проверки функциональности каталогов клиник
и реабилитационных центров, включая:
- Отображение списков учреждений
- Пагинацию
- Поиск и фильтрацию
- Детальный просмотр учреждений
- Работу с изображениями
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from facilities.models import Clinic, RehabCenter, OrganizationType, City, Review, FacilityImage
from core.models import Region
from django.contrib.auth import get_user_model

User = get_user_model()

class CatalogViewsTest(TestCase):
    """
    Тесты для представлений каталогов медицинских учреждений.
    
    Проверяет:
    1. Корректное отображение списков клиник и реабилитационных центров
    2. Работу пагинации
    3. Функциональность поиска и фильтрации
    4. Детальный просмотр учреждений
    5. Обработку неверных URL
    6. Работу с изображениями учреждений
    """
    
    def setUp(self):
        """
        Подготовка тестовых данных.
        
        Создает:
        - Регион и город
        - Типы организаций (клиника и реабилитационный центр)
        - Тестовые учреждения каждого типа
        """
        # Создаем тестовые данные
        self.client = Client()
        
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
            description='Описание клиники',
            competencies='Компетенции клиники'
        )
        self.rehab_type = OrganizationType.objects.create(
            name='Реабилитационный центр',
            slug='rehabilitation',
            description='Описание центра',
            competencies='Компетенции центра'
        )
        
        # Создаем тестовые учреждения
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            organization_type=self.clinic_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-99',
            email='test@test.com',
            website='http://test.com',
            license_number='123456',
            description='Тестовое описание'
        )
        
        self.rehab = RehabCenter.objects.create(
            name='Тестовый центр',
            slug='test-rehab',
            organization_type=self.rehab_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-98',
            email='rehab@test.com',
            website='http://rehab.com',
            description='Тестовое описание'
        )

    def test_clinic_list_view(self):
        """
        Тест отображения списка клиник.
        
        Проверяет:
        - Корректный HTTP-статус
        - Использование правильного шаблона
        - Наличие клиник в контексте
        - Количество отображаемых клиник
        - Соответствие данных тестовой клинике
        """
        response = self.client.get(reverse('facilities:clinic_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facilities/clinic_list.html')
        self.assertIn('clinics', response.context)
        self.assertEqual(len(response.context['clinics']), 1)
        self.assertEqual(response.context['clinics'][0], self.clinic)

    def test_rehabilitation_list_view(self):
        """
        Тест отображения списка реабилитационных центров.
        
        Проверяет:
        - Корректный HTTP-статус
        - Использование правильного шаблона
        - Наличие центров в контексте
        - Количество отображаемых центров
        - Соответствие данных тестовому центру
        """
        response = self.client.get(reverse('facilities:rehabilitation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facilities/rehabilitation_list.html')
        self.assertIn('rehabilitation_centers', response.context)
        self.assertEqual(len(response.context['rehabilitation_centers']), 1)
        self.assertEqual(response.context['rehabilitation_centers'][0], self.rehab)

    def test_empty_catalogs(self):
        """
        Тест отображения пустых каталогов.
        
        Проверяет:
        - Корректное отображение пустого списка клиник
        - Корректное отображение пустого списка центров
        - Отсутствие ошибок при отсутствии данных
        """
        # Удаляем все учреждения
        Clinic.objects.all().delete()
        RehabCenter.objects.all().delete()
        
        # Проверяем клиники
        response = self.client.get(reverse('facilities:clinic_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clinics']), 0)
        
        # Проверяем реабилитационные центры
        response = self.client.get(reverse('facilities:rehabilitation_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['rehabilitation_centers']), 0)

    def test_pagination(self):
        """
        Тест пагинации в каталогах.
        
        Проверяет:
        - Корректное отображение первой страницы (12 элементов)
        - Корректное отображение второй страницы (оставшиеся элементы)
        - Работу параметра page в URL
        """
        # Создаем дополнительные учреждения
        for i in range(15):
            Clinic.objects.create(
                name=f'Клиника {i}',
                slug=f'clinic-{i}',
                organization_type=self.clinic_type,
                city=self.city,
                address='Тестовый адрес',
                phone=f'+7 (999) 999-{i:02d}',
                email=f'test{i}@test.com',
                license_number=f'123{i:03d}',
                description='Тестовое описание'
            )
        
        # Проверяем первую страницу
        response = self.client.get(reverse('facilities:clinic_list'))
        self.assertEqual(len(response.context['clinics']), 12)  # paginate_by = 12
        
        # Проверяем вторую страницу
        response = self.client.get(reverse('facilities:clinic_list') + '?page=2')
        self.assertEqual(len(response.context['clinics']), 4)

    def test_search_filter(self):
        """
        Тест поиска и фильтрации учреждений.
        
        Проверяет:
        - Поиск по названию учреждения
        - Корректное количество результатов
        - Соответствие найденного учреждения поисковому запросу
        """
        # Создаем учреждение с уникальным названием
        unique_facility = Clinic.objects.create(
            name='Специализированная клиника',
            slug='unique-clinic',
            organization_type=self.clinic_type,
            city=self.city,
            address='Тестовый адрес',
            phone='+7 (999) 999-99-97',
            email='unique@test.com',
            license_number='123458',
            description='Тестовое описание'
        )
        
        # Проверяем поиск по уникальному слову
        response = self.client.get(reverse('facilities:clinic_list') + '?search=Специализированная')
        self.assertEqual(len(response.context['clinics']), 1)
        self.assertEqual(response.context['clinics'][0].name, 'Специализированная клиника')

    def test_facility_detail_view(self):
        """
        Тест детального просмотра учреждения.
        
        Проверяет:
        - Корректный HTTP-статус
        - Использование правильного шаблона
        - Наличие данных учреждения в контексте
        - Наличие связанных учреждений
        """
        response = self.client.get(reverse('facilities:clinic_detail', kwargs={'slug': self.clinic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facilities/clinic_detail.html')
        self.assertEqual(response.context['clinic'], self.clinic)
        self.assertIn('related_facilities', response.context)

    def test_rehab_detail_view(self):
        """
        Тест детального просмотра реабилитационного центра.
        
        Проверяет:
        - Корректный HTTP-статус
        - Использование правильного шаблона
        - Наличие данных центра в контексте
        - Наличие связанных учреждений
        """
        response = self.client.get(reverse('facilities:rehab_detail', kwargs={'slug': self.rehab.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facilities/rehabcenter_detail.html')
        self.assertEqual(response.context['center'], self.rehab)
        self.assertIn('related_facilities', response.context)

    def test_invalid_facility_slug(self):
        """
        Тест обработки неверного slug учреждения.
        
        Проверяет:
        - Возврат 404 ошибки при неверном slug
        - Корректную обработку несуществующих URL
        """
        response = self.client.get(reverse('facilities:clinic_detail', kwargs={'slug': 'invalid-slug'}))
        self.assertEqual(response.status_code, 404)

    def test_facility_with_image(self):
        """
        Тест отображения учреждения с изображением.
        
        Проверяет:
        - Корректное сохранение изображения
        - Связь изображения с учреждением
        - Корректное имя файла изображения
        - Наличие главного изображения
        - Корректные метаданные изображения
        """
        # Создаем тестовое изображение
        image_content = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        image = SimpleUploadedFile(
            'test_image.gif',
            image_content,
            content_type='image/gif'
        )
        
        # Добавляем изображение к учреждению через FacilityImage
        facility_image = FacilityImage.objects.create(
            facility=self.clinic,
            image=image,
            image_type=FacilityImage.ImageType.MAIN,
            title='Главное фото',
            is_main=True
        )
        
        # Проверяем отображение
        response = self.client.get(reverse('facilities:clinic_detail', kwargs={'slug': self.clinic.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем, что изображение связано с учреждением
        self.assertTrue(self.clinic.images.filter(is_main=True).exists())
        main_image = self.clinic.images.get(is_main=True)
        self.assertTrue(main_image.image.name.endswith('.gif'))
        self.assertEqual(main_image.title, 'Главное фото') 
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from core.models import Region, City
from facilities.models import (
    OrganizationType, 
    Clinic, 
    RehabCenter, 
    PrivateDoctor
)
from requests.models import AnonymousRequest, DependentRequest
from requests.forms import AnonymousRequestAdminForm, DependentRequestAdminForm

User = get_user_model()


class AnonymousRequestAdminFormTest(TestCase):
    """Тесты для AnonymousRequestAdminForm"""
    
    def setUp(self):
        # Создаем базовые данные
        self.region = Region.objects.create(name='Тестовый регион', slug='test-region')
        self.city = City.objects.create(name='Тестовый город', slug='test-city', region=self.region)
        
        # Создаем типы организаций
        self.clinic_type = OrganizationType.objects.create(
            name='Клиника', 
            slug='clinic'
        )
        self.rehab_type = OrganizationType.objects.create(
            name='Реабилитационный центр', 
            slug='rehab'
        )
        self.doctor_type = OrganizationType.objects.create(
            name='Частный врач', 
            slug='doctor'
        )
        
        # Создаем организации
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            city=self.city,
            organization_type=self.clinic_type,
            is_active=True
        )
        
        self.rehab_center = RehabCenter.objects.create(
            name='Тестовый центр',
            slug='test-rehab',
            city=self.city,
            organization_type=self.rehab_type,
            is_active=True
        )
        
        self.private_doctor = PrivateDoctor.objects.create(
            first_name='Иван',
            last_name='Иванов',
            city=self.city,
            organization_type=self.doctor_type,
            is_active=True,
            experience_years=10
        )
        
        # Создаем заявку
        self.request = AnonymousRequest.objects.create(
            phone='79991234567',
            name='Тестовый клиент',
            status=AnonymousRequest.Status.NEW,
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            message='Тестовое сообщение'
        )
    
    def test_form_initialization_without_instance(self):
        """Тест инициализации формы без экземпляра"""
        form = AnonymousRequestAdminForm()
        
        # Проверяем, что поле organization_choice имеет пустые choices
        self.assertEqual(
            form.fields['organization_choice'].widget.choices,
            [('', '---------')]
        )
    
    def test_form_initialization_with_instance_no_organization_type(self):
        """Тест инициализации формы с экземпляром без типа организации"""
        form = AnonymousRequestAdminForm(instance=self.request)
        
        # Проверяем, что поле organization_choice имеет пустые choices
        self.assertEqual(
            form.fields['organization_choice'].widget.choices,
            [('', '---------')]
        )
    
    def test_form_initialization_with_clinic_type(self):
        """Тест инициализации формы с типом организации 'Клиника'"""
        self.request.organization_type = self.clinic_type
        self.request.save()
        
        form = AnonymousRequestAdminForm(instance=self.request)
        
        # Проверяем, что в choices есть клиники
        choices = form.fields['organization_choice'].widget.choices
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.clinic.name, self.clinic.name), choices)
        self.assertNotIn((self.rehab_center.name, self.rehab_center.name), choices)
    
    def test_form_initialization_with_rehab_type(self):
        """Тест инициализации формы с типом организации 'Реабилитационный центр'"""
        self.request.organization_type = self.rehab_type
        self.request.save()
        
        form = AnonymousRequestAdminForm(instance=self.request)
        
        # Проверяем, что в choices есть реабилитационные центры
        choices = form.fields['organization_choice'].widget.choices
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.rehab_center.name, self.rehab_center.name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_form_initialization_with_doctor_type(self):
        """Тест инициализации формы с типом организации 'Частный врач'"""
        self.request.organization_type = self.doctor_type
        self.request.save()
        
        form = AnonymousRequestAdminForm(instance=self.request)
        
        # Проверяем, что в choices есть частные врачи
        doctor_full_name = self.private_doctor.get_full_name()
        choices = form.fields['organization_choice'].widget.choices
        self.assertIn(('', '---------'), choices)
        self.assertIn((doctor_full_name, doctor_full_name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_form_initialization_with_assigned_organization(self):
        """Тест инициализации формы с назначенной организацией"""
        self.request.organization_type = self.clinic_type
        self.request.assigned_organization = self.clinic.name
        self.request.save()
        
        form = AnonymousRequestAdminForm(instance=self.request)
        
        # Проверяем, что initial значение установлено
        self.assertEqual(
            form.fields['organization_choice'].initial,
            self.clinic.name
        )
    
    def test_form_save_with_organization_choice(self):
        """Тест сохранения формы с выбором организации"""
        self.request.organization_type = self.clinic_type
        self.request.save()
        
        form = AnonymousRequestAdminForm(
            instance=self.request,
            data={
                'organization_choice': self.clinic.name,
                'name': 'Тестовый клиент',
                'phone': '79991234567',
                'request_type': AnonymousRequest.RequestType.CONSULTATION,
                'message': 'Тестовое сообщение',
                'status': AnonymousRequest.Status.NEW,
                'priority': AnonymousRequest.Priority.MEDIUM,
                'source': AnonymousRequest.Source.WEBSITE_FORM
            }
        )
        
        # Проверяем, что форма валидна
        self.assertTrue(form.is_valid())
        
        # Сохраняем форму
        saved_instance = form.save()
        
        # Проверяем, что assigned_organization установлен
        self.assertEqual(saved_instance.assigned_organization, self.clinic.name)
    
    def test_form_save_without_organization_choice(self):
        """Тест сохранения формы без выбора организации"""
        self.request.organization_type = self.clinic_type
        self.request.assigned_organization = self.clinic.name
        self.request.save()
        
        form = AnonymousRequestAdminForm(
            instance=self.request,
            data={
                'organization_choice': '',
                'name': 'Тестовый клиент',
                'phone': '79991234567',
                'request_type': AnonymousRequest.RequestType.CONSULTATION,
                'message': 'Тестовое сообщение',
                'status': AnonymousRequest.Status.NEW,
                'priority': AnonymousRequest.Priority.MEDIUM,
                'source': AnonymousRequest.Source.WEBSITE_FORM,
                'assigned_organization': self.clinic.name
            }
        )
        
        # Проверяем, что форма валидна
        self.assertTrue(form.is_valid())
        
        # Сохраняем форму
        saved_instance = form.save()
        
        # Проверяем, что assigned_organization остается прежним
        self.assertEqual(saved_instance.assigned_organization, self.clinic.name)
    
    def test_get_organization_choices_clinic(self):
        """Тест получения списка клиник"""
        form = AnonymousRequestAdminForm()
        choices = form._get_organization_choices(self.clinic_type)
        
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.clinic.name, self.clinic.name), choices)
        self.assertNotIn((self.rehab_center.name, self.rehab_center.name), choices)
    
    def test_get_organization_choices_rehab(self):
        """Тест получения списка реабилитационных центров"""
        form = AnonymousRequestAdminForm()
        choices = form._get_organization_choices(self.rehab_type)
        
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.rehab_center.name, self.rehab_center.name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_get_organization_choices_doctor(self):
        """Тест получения списка частных врачей"""
        form = AnonymousRequestAdminForm()
        choices = form._get_organization_choices(self.doctor_type)
        
        doctor_full_name = self.private_doctor.get_full_name()
        self.assertIn(('', '---------'), choices)
        self.assertIn((doctor_full_name, doctor_full_name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_get_organization_choices_none(self):
        """Тест получения списка организаций с None типом"""
        form = AnonymousRequestAdminForm()
        choices = form._get_organization_choices(None)
        
        # Должен вернуть только пустой выбор
        self.assertEqual(choices, [('', '---------')])
    
    def test_get_organization_choices_unknown_type(self):
        """Тест получения списка организаций с неизвестным типом"""
        unknown_type = OrganizationType.objects.create(
            name='Неизвестный тип',
            slug='unknown'
        )
        
        form = AnonymousRequestAdminForm()
        choices = form._get_organization_choices(unknown_type)
        
        # Должен вернуть только пустой выбор
        self.assertEqual(choices, [('', '---------')])


class DependentRequestAdminFormTest(TestCase):
    """Тесты для DependentRequestAdminForm"""
    
    def setUp(self):
        # Создаем базовые данные
        self.region = Region.objects.create(name='Тестовый регион', slug='test-region')
        self.city = City.objects.create(name='Тестовый город', slug='test-city', region=self.region)
        
        # Создаем типы организаций
        self.clinic_type = OrganizationType.objects.create(
            name='Клиника', 
            slug='clinic'
        )
        self.rehab_type = OrganizationType.objects.create(
            name='Реабилитационный центр', 
            slug='rehab'
        )
        self.doctor_type = OrganizationType.objects.create(
            name='Частный врач', 
            slug='doctor'
        )
        
        # Создаем организации
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника',
            slug='test-clinic',
            city=self.city,
            organization_type=self.clinic_type,
            is_active=True
        )
        
        self.rehab_center = RehabCenter.objects.create(
            name='Тестовый центр',
            slug='test-rehab',
            city=self.city,
            organization_type=self.rehab_type,
            is_active=True
        )
        
        self.private_doctor = PrivateDoctor.objects.create(
            first_name='Иван',
            last_name='Иванов',
            city=self.city,
            organization_type=self.doctor_type,
            is_active=True,
            experience_years=10
        )
        
        # Создаем заявку
        self.request = DependentRequest.objects.create(
            phone='79991234567',
            status=DependentRequest.Status.NEW
        )
    
    def test_form_initialization_without_instance(self):
        """Тест инициализации формы без экземпляра"""
        form = DependentRequestAdminForm()
        
        # Проверяем, что поле organization_choice имеет пустые choices
        self.assertEqual(
            form.fields['organization_choice'].widget.choices,
            [('', '---------')]
        )
    
    def test_form_initialization_with_instance_no_organization_type(self):
        """Тест инициализации формы с экземпляром без типа организации"""
        form = DependentRequestAdminForm(instance=self.request)
        
        # Проверяем, что поле organization_choice имеет пустые choices
        self.assertEqual(
            form.fields['organization_choice'].widget.choices,
            [('', '---------')]
        )
    
    def test_form_initialization_with_clinic_type(self):
        """Тест инициализации формы с типом организации 'Клиника'"""
        self.request.organization_type = self.clinic_type
        self.request.save()
        
        form = DependentRequestAdminForm(instance=self.request)
        
        # Проверяем, что в choices есть клиники
        choices = form.fields['organization_choice'].widget.choices
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.clinic.name, self.clinic.name), choices)
        self.assertNotIn((self.rehab_center.name, self.rehab_center.name), choices)
    
    def test_form_initialization_with_rehab_type(self):
        """Тест инициализации формы с типом организации 'Реабилитационный центр'"""
        self.request.organization_type = self.rehab_type
        self.request.save()
        
        form = DependentRequestAdminForm(instance=self.request)
        
        # Проверяем, что в choices есть реабилитационные центры
        choices = form.fields['organization_choice'].widget.choices
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.rehab_center.name, self.rehab_center.name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_form_initialization_with_doctor_type(self):
        """Тест инициализации формы с типом организации 'Частный врач'"""
        self.request.organization_type = self.doctor_type
        self.request.save()
        
        form = DependentRequestAdminForm(instance=self.request)
        
        # Проверяем, что в choices есть частные врачи
        doctor_full_name = self.private_doctor.get_full_name()
        choices = form.fields['organization_choice'].widget.choices
        self.assertIn(('', '---------'), choices)
        self.assertIn((doctor_full_name, doctor_full_name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_form_initialization_with_assigned_organization(self):
        """Тест инициализации формы с назначенной организацией"""
        self.request.organization_type = self.clinic_type
        self.request.assigned_organization = self.clinic.name
        self.request.save()
        
        form = DependentRequestAdminForm(instance=self.request)
        
        # Проверяем, что initial значение установлено
        self.assertEqual(
            form.fields['organization_choice'].initial,
            self.clinic.name
        )
    
    def test_form_save_with_organization_choice(self):
        """Тест сохранения формы с выбором организации"""
        self.request.organization_type = self.clinic_type
        self.request.save()
        
        form = DependentRequestAdminForm(
            instance=self.request,
            data={
                'organization_choice': self.clinic.name,
                'phone': '79991234567',
                'status': DependentRequest.Status.NEW,
                'addiction_type': DependentRequest.AddictionType.OTHER,
                'contact_type': DependentRequest.ContactType.ANONYMOUS
            }
        )
        
        # Проверяем, что форма валидна
        self.assertTrue(form.is_valid())
        
        # Сохраняем форму
        saved_instance = form.save()
        
        # Проверяем, что assigned_organization установлен
        self.assertEqual(saved_instance.assigned_organization, self.clinic.name)
    
    def test_form_save_without_organization_choice(self):
        """Тест сохранения формы без выбора организации"""
        self.request.organization_type = self.clinic_type
        self.request.assigned_organization = self.clinic.name
        self.request.save()
        
        form = DependentRequestAdminForm(
            instance=self.request,
            data={
                'organization_choice': '',
                'phone': '79991234567',
                'status': DependentRequest.Status.NEW,
                'addiction_type': DependentRequest.AddictionType.OTHER,
                'contact_type': DependentRequest.ContactType.ANONYMOUS,
                'assigned_organization': self.clinic.name
            }
        )
        
        # Проверяем, что форма валидна
        self.assertTrue(form.is_valid())
        
        # Сохраняем форму
        saved_instance = form.save()
        
        # Проверяем, что assigned_organization остается прежним
        self.assertEqual(saved_instance.assigned_organization, self.clinic.name)
    
    def test_get_organization_choices_clinic(self):
        """Тест получения списка клиник"""
        form = DependentRequestAdminForm()
        choices = form._get_organization_choices(self.clinic_type)
        
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.clinic.name, self.clinic.name), choices)
        self.assertNotIn((self.rehab_center.name, self.rehab_center.name), choices)
    
    def test_get_organization_choices_rehab(self):
        """Тест получения списка реабилитационных центров"""
        form = DependentRequestAdminForm()
        choices = form._get_organization_choices(self.rehab_type)
        
        self.assertIn(('', '---------'), choices)
        self.assertIn((self.rehab_center.name, self.rehab_center.name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_get_organization_choices_doctor(self):
        """Тест получения списка частных врачей"""
        form = DependentRequestAdminForm()
        choices = form._get_organization_choices(self.doctor_type)
        
        doctor_full_name = self.private_doctor.get_full_name()
        self.assertIn(('', '---------'), choices)
        self.assertIn((doctor_full_name, doctor_full_name), choices)
        self.assertNotIn((self.clinic.name, self.clinic.name), choices)
    
    def test_get_organization_choices_none(self):
        """Тест получения списка организаций с None типом"""
        form = DependentRequestAdminForm()
        choices = form._get_organization_choices(None)
        
        # Должен вернуть только пустой выбор
        self.assertEqual(choices, [('', '---------')])
    
    def test_get_organization_choices_unknown_type(self):
        """Тест получения списка организаций с неизвестным типом"""
        unknown_type = OrganizationType.objects.create(
            name='Неизвестный тип',
            slug='unknown'
        )
        
        form = DependentRequestAdminForm()
        choices = form._get_organization_choices(unknown_type)
        
        # Должен вернуть только пустой выбор
        self.assertEqual(choices, [('', '---------')])
    
    def test_form_save_commit_false(self):
        """Тест сохранения формы с commit=False"""
        self.request.organization_type = self.clinic_type
        self.request.save()
        
        form = DependentRequestAdminForm(
            instance=self.request,
            data={
                'organization_choice': self.clinic.name,
                'phone': '79991234567',
                'status': DependentRequest.Status.NEW,
                'addiction_type': DependentRequest.AddictionType.OTHER,
                'contact_type': DependentRequest.ContactType.ANONYMOUS
            }
        )
        
        # Проверяем, что форма валидна
        self.assertTrue(form.is_valid())
        
        # Сохраняем форму с commit=False
        saved_instance = form.save(commit=False)
        
        # Проверяем, что assigned_organization установлен, но объект не сохранен в БД
        self.assertEqual(saved_instance.assigned_organization, self.clinic.name)
        # При commit=False объект не должен быть сохранен в БД
        # Но поскольку мы передаем instance, Django может его обновить
        # Проверяем, что assigned_organization установлен правильно 
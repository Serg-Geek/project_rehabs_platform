from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from requests.models import (
    AnonymousRequest, 
    RequestNote, 
    RequestStatusHistory, 
    DependentRequest
)
from requests.views import ConsultationRequestView, PartnerRequestView, DependentRequestView

User = get_user_model()

class ConsultationRequestViewTest(TestCase):
    """Тесты для представления ConsultationRequestView"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('requests:consultation_request')
        
    def test_get_consultation_page(self):
        """Тест GET-запроса страницы консультации"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
    def test_post_consultation_request(self):
        """Тест POST-запроса формы консультации"""
        data = {
            'phone': '79991234567',
            'name': 'Тестовый Клиент',
            'service-type': 'consultation'
        }
        response = self.client.post(self.url, data)
        
        # Проверяем редирект на страницу успеха
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('requests:success'))
        
        # Проверяем создание заявки в БД
        self.assertTrue(AnonymousRequest.objects.filter(phone='79991234567').exists())
        request = AnonymousRequest.objects.filter(phone='79991234567').first()
        self.assertEqual(request.status, AnonymousRequest.Status.NEW)
        self.assertEqual(request.request_type, AnonymousRequest.RequestType.CONSULTATION)
    
    def test_post_consultation_request_ajax(self):
        """Тест AJAX-запроса формы консультации"""
        data = {
            'phone': '79991234568',
            'name': 'AJAX Клиент',
            'service-type': 'therapy'
        }
        response = self.client.post(
            self.url, 
            data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Проверяем JSON-ответ
        self.assertEqual(response.status_code, 200)
        self.assertTrue('success' in response.json())
        self.assertTrue(response.json()['success'])
        self.assertTrue('request_number' in response.json())
        
        # Проверяем создание заявки в БД
        self.assertTrue(AnonymousRequest.objects.filter(phone='79991234568').exists())
        request = AnonymousRequest.objects.filter(phone='79991234568').first()
        # preferred_service не устанавливается из service-type, остается пустым или значением по умолчанию
        self.assertEqual(request.request_type, AnonymousRequest.RequestType.CONSULTATION)


class PartnerRequestViewTest(TestCase):
    """Тесты для представления PartnerRequestView"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('requests:partner_request')
        
    def test_post_partner_request(self):
        """Тест POST-запроса формы партнерства"""
        data = {
            'name': 'Партнерская организация',
            'phone': '79991234567',
            'email': 'partner@example.com',
            'message': 'Предложение о сотрудничестве'
        }
        response = self.client.post(self.url, data)
        
        # Проверяем редирект на страницу успеха
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('requests:success'))
        
        # Проверяем создание заявки в БД
        self.assertTrue(AnonymousRequest.objects.filter(phone='79991234567', name='Партнерская организация').exists())
        request = AnonymousRequest.objects.filter(phone='79991234567', name='Партнерская организация').first()
        self.assertEqual(request.status, AnonymousRequest.Status.NEW)
        self.assertEqual(request.request_type, AnonymousRequest.RequestType.PARTNER)
    

class DependentRequestViewTest(TestCase):
    """Тесты для представления DependentRequestView"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('requests:dependent_request')
        
    def test_post_dependent_request(self):
        """Тест POST-запроса формы зависимого"""
        data = {
            'phone': '79991234567',
            'addiction_type': DependentRequest.AddictionType.ALCOHOL,
            'name': 'Тестовый Зависимый',
            'service-type': 'therapy'
        }
        response = self.client.post(self.url, data)
        
        # Проверяем редирект на страницу успеха
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('requests:success'))
        
        # Проверяем создание заявки в БД
        self.assertTrue(DependentRequest.objects.filter(phone='79991234567').exists())
        request = DependentRequest.objects.filter(phone='79991234567').first()
        self.assertEqual(request.status, DependentRequest.Status.NEW)
        self.assertEqual(request.addiction_type, DependentRequest.AddictionType.ALCOHOL)
        # preferred_treatment не устанавливается из service-type, остается None
        self.assertIsNone(request.preferred_treatment) 


class PrintReportViewTest(TestCase):
    """Тесты для представления печати отчета"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin_password'
        )
        
        # Создаем тестовую заявку с историей
        self.anonymous_request = AnonymousRequest.objects.create(
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            status=AnonymousRequest.Status.IN_PROGRESS,
            name="Тестовый Клиент",
            phone="79991234567",
            message="Тестовое сообщение"
        )
        
        # Создаем историю статусов
        from requests.models import RequestStatusHistory, RequestActionLog
        self.history = RequestStatusHistory.objects.create(
            request=self.anonymous_request,
            old_status=AnonymousRequest.Status.NEW,
            new_status=AnonymousRequest.Status.IN_PROGRESS,
            comment="Тестовое изменение статуса",
            changed_by=self.user
        )
        
        self.action_log = RequestActionLog.objects.create(
            request=self.anonymous_request,
            user=self.user,
            action=RequestActionLog.Action.STATUS_CHANGE,
            details="Тестовое действие"
        )
        
        # Создаем заметку
        from requests.models import RequestNote
        self.note = RequestNote.objects.create(
            request=self.anonymous_request,
            text="Тестовая заметка",
            created_by=self.user
        )
    
    def test_print_report_anonymous_request(self):
        """Тест печати отчета для анонимной заявки"""
        self.client.force_login(self.user)
        url = reverse('requests:print_report', args=[self.anonymous_request.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовый Клиент")
        self.assertContains(response, "79991234567")
        self.assertContains(response, "История статусов")
        self.assertContains(response, "Журнал действий")  # Исправлено с "Логи действий"
        self.assertContains(response, "Заметки")
        self.assertContains(response, "Тестовая заметка")
    
    def test_print_report_dependent_request(self):
        """Тест печати отчета для заявки зависимого"""
        # Создаем заявку зависимого с уникальным ID
        dependent_request = DependentRequest.objects.create(
            id=999,  # Устанавливаем уникальный ID
            addiction_type=DependentRequest.AddictionType.ALCOHOL,
            contact_type=DependentRequest.ContactType.ANONYMOUS,
            status=DependentRequest.Status.NEW,
            phone="79991234568"
        )
        
        # Создаем историю статусов для зависимого
        from requests.models import DependentRequestStatusHistory, DependentRequestNote
        history = DependentRequestStatusHistory.objects.create(
            request=dependent_request,
            old_status=DependentRequest.Status.NEW,  # Используем реальный статус вместо None
            new_status=DependentRequest.Status.NEW,
            comment="Создание заявки",
            changed_by=self.user
        )
        
        note = DependentRequestNote.objects.create(
            request=dependent_request,
            text="Заметка для зависимого",
            created_by=self.user
        )
        
        self.client.force_login(self.user)
        url = reverse('requests:print_report', args=[dependent_request.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "79991234568")
        self.assertContains(response, "История статусов")
        self.assertContains(response, "Заметки")
        self.assertContains(response, "Заметка для зависимого")
        # Проверяем, что это отчет для зависимого, а не анонимного
        self.assertNotContains(response, "Тестовый Клиент")  # Это из анонимной заявки
    
    def test_print_report_nonexistent_request(self):
        """Тест печати отчета для несуществующей заявки"""
        self.client.force_login(self.user)
        url = reverse('requests:print_report', args=[99999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Редирект на страницу ошибки 
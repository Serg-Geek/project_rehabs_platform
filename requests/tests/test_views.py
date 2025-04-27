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
        self.assertEqual(request.preferred_service, 'Терапия')


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
        self.assertEqual(request.preferred_treatment, 'Терапия') 
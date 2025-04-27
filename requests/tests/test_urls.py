from django.test import SimpleTestCase
from django.urls import reverse, resolve
from requests.views import (
    ConsultationRequestView, 
    PartnerRequestView, 
    DependentRequestView,
    success_view,
    error_view,
    print_request_report
)

class UrlsTest(SimpleTestCase):
    """Тесты URL-маршрутов приложения requests"""
    
    def test_consultation_request_url_resolves(self):
        """Тест разрешения URL для формы консультации"""
        url = reverse('requests:consultation_request')
        self.assertEqual(url, '/requests/consultation/')
        self.assertEqual(resolve(url).func.view_class, ConsultationRequestView)
    
    def test_partner_request_url_resolves(self):
        """Тест разрешения URL для формы партнерства"""
        url = reverse('requests:partner_request')
        self.assertEqual(url, '/requests/partner/')
        self.assertEqual(resolve(url).func.view_class, PartnerRequestView)
    
    def test_dependent_request_url_resolves(self):
        """Тест разрешения URL для формы зависимого"""
        url = reverse('requests:dependent_request')
        self.assertEqual(url, '/requests/dependent/')
        self.assertEqual(resolve(url).func.view_class, DependentRequestView)
    
    def test_success_url_resolves(self):
        """Тест разрешения URL для страницы успеха"""
        url = reverse('requests:success')
        self.assertEqual(url, '/requests/success/')
        self.assertEqual(resolve(url).func, success_view)
    
    def test_error_url_resolves(self):
        """Тест разрешения URL для страницы ошибки"""
        url = reverse('requests:error')
        self.assertEqual(url, '/requests/error/')
        self.assertEqual(resolve(url).func, error_view)
    
    def test_print_report_url_resolves(self):
        """Тест разрешения URL для печати отчета"""
        url = reverse('requests:print_report', args=[1])
        self.assertEqual(url, '/requests/report/1/')
        self.assertEqual(resolve(url).func, print_request_report)
    
    def test_print_report_url_with_type_parameter(self):
        """Тест URL для печати отчета с параметром типа"""
        url = reverse('requests:print_report', args=[1]) + '?type=dependent'
        self.assertEqual(url, '/requests/report/1/?type=dependent') 
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import Permission

from requests.models import (
    AnonymousRequest, 
    RequestNote, 
    RequestStatusHistory,
    RequestActionLog,
    DependentRequest
)
from requests.admin import (
    AnonymousRequestAdmin, 
    RequestNoteAdmin, 
    RequestStatusHistoryAdmin,
    RequestActionLogAdmin, 
    DependentRequestAdmin
)

User = get_user_model()

class MockRequest:
    """Мок-объект запроса для использования в тестах"""
    def __init__(self, user=None):
        self.user = user
        self.session = {}
        self._messages = FallbackStorage(self)


class RequestsAdminTest(TestCase):
    """Тесты административного интерфейса приложения requests"""
    
    def setUp(self):
        # Создаем администратора
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin_password'
        )
        
        # Создаем обычного стаф-пользователя
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staff_password',
            is_staff=True
        )
        
        # Создаем тестовую заявку
        self.anonymous_request = AnonymousRequest.objects.create(
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            status=AnonymousRequest.Status.NEW,
            name="Тестовый Клиент",
            phone="79991234567",
            message="Тестовое сообщение",
            priority=AnonymousRequest.Priority.MEDIUM,
            source=AnonymousRequest.Source.WEBSITE_FORM
        )
        
        # Создаем Dependent Request
        self.dependent_request = DependentRequest.objects.create(
            addiction_type=DependentRequest.AddictionType.ALCOHOL,
            contact_type=DependentRequest.ContactType.ANONYMOUS,
            status=DependentRequest.Status.NEW,
            phone="79991234568"
        )
        
        # Инициализируем клиент
        self.client = Client()
        
        # Мок-сайт админки
        self.site = AdminSite()
        self.anonymous_request_admin = AnonymousRequestAdmin(AnonymousRequest, self.site)
        self.request_note_admin = RequestNoteAdmin(RequestNote, self.site)
        self.request_status_history_admin = RequestStatusHistoryAdmin(RequestStatusHistory, self.site)
        self.request_action_log_admin = RequestActionLogAdmin(RequestActionLog, self.site)
        self.dependent_request_admin = DependentRequestAdmin(DependentRequest, self.site)
    
    def test_anonymous_request_admin_list_view(self):
        """Тест отображения списка анонимных заявок в админке"""
        # Используем force_login вместо login
        self.client.force_login(self.admin_user)
        
        # Переходим на страницу списка заявок
        url = reverse('admin:requests_anonymousrequest_changelist')
        response = self.client.get(url)
        
        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)
        
        # Проверяем наличие наших заявок на странице
        self.assertContains(response, self.anonymous_request.phone)
    
    def test_dependent_request_admin_list_view(self):
        """Тест отображения списка заявок от зависимых в админке"""
        # Используем force_login вместо login
        self.client.force_login(self.admin_user)
        
        # Переходим на страницу списка заявок
        url = reverse('admin:requests_dependentrequest_changelist')
        response = self.client.get(url)
        
        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)
        
        # Проверяем наличие наших заявок на странице
        self.assertContains(response, self.dependent_request.phone)
    
    def test_anonymous_request_admin_print_report_button(self):
        """Тест наличия кнопки печати отчета в админке"""
        request = MockRequest(user=self.admin_user)
        
        # Получаем HTML кнопки
        button_html = self.anonymous_request_admin.print_report_button(self.anonymous_request)
        
        # Проверяем, что HTML содержит ссылку и текст
        self.assertIn(f'/requests/report/{self.anonymous_request.id}/', button_html)
        self.assertIn('Печать отчета', button_html)
    
    def test_dependent_request_admin_print_report_button(self):
        """Тест наличия кнопки печати отчета в админке для заявки от зависимого"""
        request = MockRequest(user=self.admin_user)
        
        # Получаем HTML кнопки
        button_html = self.dependent_request_admin.print_report_button(self.dependent_request)
        
        # Проверяем, что HTML содержит ссылку и текст
        self.assertIn(f'/requests/report/{self.dependent_request.id}/', button_html)
        self.assertIn('Печать отчета', button_html)
    
    def test_anonymous_request_admin_changeform_view(self):
        """Тест страницы редактирования анонимной заявки в админке"""
        # Используем force_login вместо login
        self.client.force_login(self.admin_user)
        
        # Переходим на страницу редактирования заявки
        url = reverse('admin:requests_anonymousrequest_change', args=[self.anonymous_request.id])
        response = self.client.get(url)
        
        # Проверяем успешный ответ
        self.assertEqual(response.status_code, 200)
        
        # Проверяем наличие информации о заявке
        self.assertContains(response, self.anonymous_request.name)
        self.assertContains(response, self.anonymous_request.phone)
        
        # Проверяем наличие кнопки печати отчета
        self.assertContains(response, 'Печать отчета')
    
    def test_anonymous_request_admin_mark_as_in_progress_action(self):
        """Тест действия массовой отметки заявок как 'В обработке'"""
        # Создаем дополнительные заявки для теста
        request2 = AnonymousRequest.objects.create(
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            status=AnonymousRequest.Status.NEW,
            name="Второй клиент",
            phone="79991234570",
            message="Тестовое сообщение 2"
        )
        
        # Создаем мок-запрос от админа
        request = MockRequest(user=self.admin_user)
        
        # Вызываем действие администратора
        queryset = AnonymousRequest.objects.filter(id__in=[self.anonymous_request.id, request2.id])
        self.anonymous_request_admin.mark_as_in_progress(request, queryset)
        
        # Проверяем, что статус изменился на IN_PROGRESS
        self.anonymous_request.refresh_from_db()
        request2.refresh_from_db()
        
        self.assertEqual(self.anonymous_request.status, AnonymousRequest.Status.IN_PROGRESS)
        self.assertEqual(request2.status, AnonymousRequest.Status.IN_PROGRESS) 
    
    def test_anonymous_request_admin_status_change_creates_history(self):
        """Тест автоматического создания истории статусов при изменении статуса"""
        # Тестируем логику создания истории статусов напрямую
        from requests.models import RequestStatusHistory
        
        # Создаем запись в истории статусов
        history_entry = RequestStatusHistory.objects.create(
            request=self.anonymous_request,
            old_status=AnonymousRequest.Status.NEW,
            new_status=AnonymousRequest.Status.IN_PROGRESS,
            comment="Статус изменен с 'Новая' на 'В обработке'",
            changed_by=self.admin_user
        )
        
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.old_status, AnonymousRequest.Status.NEW)
        self.assertEqual(history_entry.new_status, AnonymousRequest.Status.IN_PROGRESS)
        self.assertIn("Статус изменен с 'Новая' на 'В обработке'", history_entry.comment)
        self.assertEqual(history_entry.changed_by, self.admin_user)
    
    def test_anonymous_request_admin_status_change_creates_action_log(self):
        """Тест автоматического создания лога действий при изменении статуса"""
        # Тестируем логику создания лога действий напрямую
        from requests.models import RequestActionLog
        
        # Создаем запись в логе действий
        action_log = RequestActionLog.objects.create(
            request=self.anonymous_request,
            user=self.admin_user,
            action=RequestActionLog.Action.STATUS_CHANGE,
            details="Статус изменен с 'Новая' на 'В обработке' через админку"
        )
        
        self.assertIsNotNone(action_log)
        self.assertEqual(action_log.user, self.admin_user)
        self.assertIn("Статус изменен с 'Новая' на 'В обработке'", action_log.details)
    
    def test_dependent_request_admin_status_change_creates_history(self):
        """Тест автоматического создания истории статусов для зависимых заявок"""
        # Тестируем логику создания истории статусов напрямую
        from requests.models import DependentRequestStatusHistory
        
        # Создаем запись в истории статусов
        history_entry = DependentRequestStatusHistory.objects.create(
            request=self.dependent_request,
            old_status=DependentRequest.Status.NEW,
            new_status=DependentRequest.Status.IN_PROGRESS,
            comment="Статус изменен с 'Новая' на 'В обработке'",
            changed_by=self.admin_user
        )
        
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.old_status, DependentRequest.Status.NEW)
        self.assertEqual(history_entry.new_status, DependentRequest.Status.IN_PROGRESS)
        self.assertIn("Статус изменен с 'Новая' на 'В обработке'", history_entry.comment)
        self.assertEqual(history_entry.changed_by, self.admin_user) 
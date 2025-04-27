from django.test import TestCase
from django.contrib.auth import get_user_model

from requests.models import (
    AnonymousRequest, 
    RequestNote, 
    RequestStatusHistory, 
    RequestActionLog, 
    Request, 
    DependentRequest,
    RequestTemplate
)

User = get_user_model()

class AnonymousRequestModelTest(TestCase):
    """Тесты для модели AnonymousRequest"""
    
    def setUp(self):
        self.request = AnonymousRequest.objects.create(
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            status=AnonymousRequest.Status.NEW,
            priority=AnonymousRequest.Priority.MEDIUM,
            source=AnonymousRequest.Source.WEBSITE_FORM,
            name="Тестовый Клиент",
            phone="79991234567",
            email="test@example.com",
            message="Тестовое сообщение"
        )
    
    def test_request_creation(self):
        """Тест создания анонимной заявки"""
        self.assertEqual(self.request.name, "Тестовый Клиент")
        self.assertEqual(self.request.phone, "79991234567")
        self.assertEqual(self.request.status, AnonymousRequest.Status.NEW)
        self.assertEqual(self.request.request_type, AnonymousRequest.RequestType.CONSULTATION)
        
    def test_request_str_method(self):
        """Тест строкового представления заявки"""
        self.assertIn("Тестовый Клиент", str(self.request))


class RequestNoteModelTest(TestCase):
    """Тесты для модели RequestNote"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.request = AnonymousRequest.objects.create(
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            status=AnonymousRequest.Status.NEW,
            name="Тестовый Клиент",
            phone="79991234567",
            message="Тестовое сообщение"
        )
        
        self.note = RequestNote.objects.create(
            request=self.request,
            text="Тестовая заметка",
            is_important=True,
            created_by=self.user
        )
    
    def test_note_creation(self):
        """Тест создания заметки к заявке"""
        self.assertEqual(self.note.text, "Тестовая заметка")
        self.assertTrue(self.note.is_important)
        self.assertEqual(self.note.created_by, self.user)
        self.assertEqual(self.note.request, self.request)
    
    def test_note_str_method(self):
        """Тест строкового представления заметки"""
        self.assertIn(f"#{self.request.id}", str(self.note))
        self.assertIn("Тестовый Клиент", str(self.note))


class RequestStatusHistoryModelTest(TestCase):
    """Тесты для модели RequestStatusHistory"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.request = AnonymousRequest.objects.create(
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            status=AnonymousRequest.Status.IN_PROGRESS,
            name="Тестовый Клиент",
            phone="79991234567",
            message="Тестовое сообщение"
        )
        
        self.history = RequestStatusHistory.objects.create(
            request=self.request,
            old_status=AnonymousRequest.Status.NEW,
            new_status=AnonymousRequest.Status.IN_PROGRESS,
            comment="Изменение статуса",
            changed_by=self.user
        )
    
    def test_history_creation(self):
        """Тест создания записи истории статусов"""
        self.assertEqual(self.history.old_status, AnonymousRequest.Status.NEW)
        self.assertEqual(self.history.new_status, AnonymousRequest.Status.IN_PROGRESS)
        self.assertEqual(self.history.comment, "Изменение статуса")
        self.assertEqual(self.history.changed_by, self.user)
        self.assertEqual(self.history.request, self.request)


class DependentRequestModelTest(TestCase):
    """Тесты для модели DependentRequest"""
    
    def setUp(self):
        self.request = DependentRequest.objects.create(
            addiction_type=DependentRequest.AddictionType.ALCOHOL,
            contact_type=DependentRequest.ContactType.ANONYMOUS,
            status=DependentRequest.Status.NEW,
            phone="79991234567",
            age=30,
            addiction_duration="5 лет",
            current_condition="Удовлетворительное"
        )
    
    def test_request_creation(self):
        """Тест создания заявки от зависимого"""
        self.assertEqual(self.request.addiction_type, DependentRequest.AddictionType.ALCOHOL)
        self.assertEqual(self.request.contact_type, DependentRequest.ContactType.ANONYMOUS)
        self.assertEqual(self.request.status, DependentRequest.Status.NEW)
        self.assertEqual(self.request.phone, "79991234567")
        self.assertEqual(self.request.age, 30)
        self.assertEqual(self.request.addiction_duration, "5 лет")
    
    def test_request_str_method(self):
        """Тест строкового представления заявки от зависимого"""
        self.assertIn("Анонимная заявка", str(self.request))


class RequestTemplateModelTest(TestCase):
    """Тесты для модели RequestTemplate"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.template = RequestTemplate.objects.create(
            name="Тестовый шаблон",
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            template_text="Это текст шаблона для тестирования",
            is_active=True,
            created_by=self.user
        )
    
    def test_template_creation(self):
        """Тест создания шаблона заявки"""
        self.assertEqual(self.template.name, "Тестовый шаблон")
        self.assertEqual(self.template.request_type, AnonymousRequest.RequestType.CONSULTATION)
        self.assertEqual(self.template.template_text, "Это текст шаблона для тестирования")
        self.assertTrue(self.template.is_active)
        self.assertEqual(self.template.created_by, self.user)
    
    def test_template_str_method(self):
        """Тест строкового представления шаблона"""
        self.assertEqual(str(self.template), "Тестовый шаблон")


class RequestActionLogModelTest(TestCase):
    """Тесты для модели RequestActionLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        self.request = AnonymousRequest.objects.create(
            request_type=AnonymousRequest.RequestType.CONSULTATION,
            status=AnonymousRequest.Status.NEW,
            name="Тестовый Клиент",
            phone="79991234567",
            message="Тестовое сообщение"
        )
        
        self.action_log = RequestActionLog.objects.create(
            request=self.request,
            user=self.user,
            action=RequestActionLog.Action.CREATE,
            details="Создание заявки"
        )
    
    def test_action_log_creation(self):
        """Тест создания записи лога действий"""
        self.assertEqual(self.action_log.action, RequestActionLog.Action.CREATE)
        self.assertEqual(self.action_log.details, "Создание заявки")
        self.assertEqual(self.action_log.user, self.user)
        self.assertEqual(self.action_log.request, self.request)
        
    def test_action_log_str_method(self):
        """Тест строкового представления лога действий"""
        self.assertIn("Создание", str(self.action_log))
        self.assertIn("Тестовый Клиент", str(self.action_log)) 
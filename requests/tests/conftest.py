import pytest
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertTemplateUsed

from requests.models import (
    AnonymousRequest, 
    DependentRequest,
    RequestNote,
    RequestStatusHistory,
    RequestActionLog
)

User = get_user_model()

@pytest.fixture
def admin_user():
    """Фикстура для создания администратора"""
    return User.objects.create_superuser(
        username='admin_fixture',
        email='admin_fixture@example.com',
        password='admin_password'
    )

@pytest.fixture
def staff_user():
    """Фикстура для создания сотрудника"""
    return User.objects.create_user(
        username='staff_fixture',
        email='staff_fixture@example.com',
        password='staff_password',
        is_staff=True
    )

@pytest.fixture
def regular_user():
    """Фикстура для создания обычного пользователя"""
    return User.objects.create_user(
        username='user_fixture',
        email='user_fixture@example.com',
        password='user_password'
    )

@pytest.fixture
def anonymous_request():
    """Фикстура для создания анонимной заявки"""
    return AnonymousRequest.objects.create(
        request_type=AnonymousRequest.RequestType.CONSULTATION,
        status=AnonymousRequest.Status.NEW,
        priority=AnonymousRequest.Priority.MEDIUM,
        source=AnonymousRequest.Source.WEBSITE_FORM,
        name="Тестовый Клиент Фикстура",
        phone="79991234599",
        message="Тестовое сообщение из фикстуры"
    )

@pytest.fixture
def dependent_request():
    """Фикстура для создания заявки от зависимого"""
    return DependentRequest.objects.create(
        addiction_type=DependentRequest.AddictionType.ALCOHOL,
        contact_type=DependentRequest.ContactType.ANONYMOUS,
        status=DependentRequest.Status.NEW,
        phone="79991234598",
        age=35,
        addiction_duration="7 лет"
    )

@pytest.fixture
def request_note(anonymous_request, staff_user):
    """Фикстура для создания заметки к заявке"""
    return RequestNote.objects.create(
        request=anonymous_request,
        text="Тестовая заметка из фикстуры",
        is_important=True,
        created_by=staff_user
    )

@pytest.fixture
def request_status_history(anonymous_request, staff_user):
    """Фикстура для создания истории статусов"""
    return RequestStatusHistory.objects.create(
        request=anonymous_request,
        old_status=AnonymousRequest.Status.NEW,
        new_status=AnonymousRequest.Status.IN_PROGRESS,
        comment="Изменение статуса из фикстуры",
        changed_by=staff_user
    )

@pytest.fixture
def request_action_log(anonymous_request, staff_user):
    """Фикстура для создания записи в логе действий"""
    return RequestActionLog.objects.create(
        request=anonymous_request,
        user=staff_user,
        action=RequestActionLog.Action.STATUS_CHANGE,
        details="Действие из фикстуры"
    ) 
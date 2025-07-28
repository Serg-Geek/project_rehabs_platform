from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

from admin_logs.models import AdminActionLog, AccessLevel
from facilities.models import Clinic, OrganizationType
from core.models import City, Region

User = get_user_model()

class AdminLogsModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            role='superuser'
        )
        
        # Создаем уровень доступа
        self.access_level = AccessLevel.objects.create(
            name='Суперюзер',
            code='superuser',
            level_type=AccessLevel.LevelType.SUPERUSER,
            description='Полный доступ к системе',
            is_active=True,
            created_by=self.user
        )
        
        self.region = Region.objects.create(name='Тестовый регион', slug='test-region')
        self.city = City.objects.create(name='Тестовый город', slug='test-city', region=self.region)
        self.organization_type = OrganizationType.objects.create(
            name='Клиника', slug='clinic', description='Медицинская клиника')
        self.clinic = Clinic.objects.create(
            name='Тестовая клиника', city=self.city, address='Тестовый адрес',
            phone='+7 (999) 999-99-99', email='test@test.com', organization_type=self.organization_type)
        
        self.admin_log = AdminActionLog.objects.create(
            user=self.user,
            action='create',
            app_label='facilities',
            model_name='Clinic',
            object_id=self.clinic.id,
            access_level=self.access_level,
            ip_address='127.0.0.1'
        )

    def test_admin_action_log_creation(self):
        self.assertEqual(self.admin_log.user, self.user)
        self.assertEqual(self.admin_log.action, 'create')
        self.assertEqual(self.admin_log.app_label, 'facilities')
        self.assertEqual(self.admin_log.model_name, 'Clinic')
        self.assertEqual(self.admin_log.access_level, self.access_level)
        self.assertEqual(self.admin_log.ip_address, '127.0.0.1')

    def test_admin_action_log_str_representation(self):
        expected = f"{self.user} - {self.admin_log.action} - {self.admin_log.created_at}"
        self.assertEqual(str(self.admin_log), expected)

    def test_admin_action_log_meta_ordering(self):
        self.assertEqual(AdminActionLog._meta.ordering, ['-created_at'])

    def test_admin_action_log_verbose_names(self):
        self.assertEqual(AdminActionLog._meta.verbose_name, 'Лог действий администратора')
        self.assertEqual(AdminActionLog._meta.verbose_name_plural, 'Логи действий администраторов')

    def test_admin_action_log_field_verbose_names(self):
        action_field = AdminActionLog._meta.get_field('action')
        app_label_field = AdminActionLog._meta.get_field('app_label')
        ip_address_field = AdminActionLog._meta.get_field('ip_address')
        
        self.assertEqual(action_field.verbose_name, 'Действие')
        self.assertEqual(app_label_field.verbose_name, 'Приложение')
        self.assertEqual(ip_address_field.verbose_name, 'IP-адрес')

    def test_access_level_creation(self):
        self.assertEqual(self.access_level.name, 'Суперюзер')
        self.assertEqual(self.access_level.code, 'superuser')
        self.assertEqual(self.access_level.level_type, AccessLevel.LevelType.SUPERUSER)
        self.assertTrue(self.access_level.is_active)

    def test_access_level_str_representation(self):
        self.assertEqual(str(self.access_level), 'Суперюзер')

    def test_access_level_verbose_names(self):
        self.assertEqual(AccessLevel._meta.verbose_name, 'Уровень доступа')
        self.assertEqual(AccessLevel._meta.verbose_name_plural, 'Уровни доступа') 
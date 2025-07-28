from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import User, UserProfile


class UserModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='content_admin'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'content_admin')
        self.assertFalse(user.is_staff)  # Обычный пользователь НЕ должен быть staff
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        superuser = self.User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.role, 'superuser')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.check_password('adminpass123'))

    def test_create_user_without_email(self):
        """Тест создания пользователя без email"""
        with self.assertRaises(ValueError):
            self.User.objects.create_user(
                username='testuser',
                email='',
                password='testpass123'
            )

    def test_create_user_without_username(self):
        """Тест создания пользователя без username"""
        with self.assertRaises(ValueError):
            self.User.objects.create_user(
                username='',
                email='test@example.com',
                password='testpass123'
            )

    def test_user_role_validation(self):
        """Тест валидации роли пользователя"""
        user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='content_admin'
        )
        self.assertTrue(user.has_role('content_admin'))
        self.assertFalse(user.has_role('superuser'))

    def test_user_permissions(self):
        """Тест проверки прав доступа"""
        # Создаем пользователя с ролью content_admin
        user = self.User.objects.create_user(
            username='content_admin',
            email='content@example.com',
            password='testpass123',
            role='content_admin'
        )
        self.assertTrue(user.is_content_admin())
        self.assertFalse(user.is_requests_admin())

        # Создаем пользователя с ролью requests_admin
        user = self.User.objects.create_user(
            username='requests_admin',
            email='requests@example.com',
            password='testpass123',
            role='requests_admin'
        )
        self.assertFalse(user.is_content_admin())
        self.assertTrue(user.is_requests_admin())

        # Создаем суперпользователя
        superuser = self.User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='testpass123'
        )
        self.assertTrue(superuser.is_content_admin())
        self.assertTrue(superuser.is_requests_admin())

    def test_email_normalization(self):
        """Тест нормализации email"""
        email = 'test@EXAMPLE.COM'
        user = self.User.objects.create_user(
            username='testuser',
            email=email,
            password='testpass123'
        )
        self.assertEqual(user.email, email.lower())

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(str(user), 'Test User')

        # Если имя и фамилия не указаны
        user = self.User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser2')


class UserProfileTests(TestCase):
    def setUp(self):
        """Создаем пользователя для тестов"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_created_automatically(self):
        """Тест автоматического создания профиля при создании пользователя"""
        self.assertIsNotNone(self.user.profile)
        self.assertEqual(self.user.profile.user, self.user)

    def test_profile_str_representation(self):
        """Тест строкового представления профиля"""
        self.assertEqual(str(self.user.profile), f"Профиль {self.user.email}")

    def test_profile_update(self):
        """Тест обновления профиля"""
        profile = self.user.profile
        profile.bio = 'Updated Bio'
        profile.gender = 'male'
        profile.save()

        # Проверяем, что изменения сохранились
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, 'Updated Bio')
        self.assertEqual(updated_profile.gender, 'male') 
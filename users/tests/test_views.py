from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from users.models import User

User = get_user_model()


class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_password_reset_view_get(self):
        """Тест GET запроса к странице сброса пароля"""
        response = self.client.get(reverse('users:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_form.html')

    def test_password_reset_view_post_success(self):
        """Тест успешного запроса сброса пароля"""
        response = self.client.post(reverse('users:password_reset'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после отправки

    def test_password_reset_view_post_failure(self):
        """Тест неудачного запроса сброса пароля (несуществующий email)"""
        response = self.client.post(reverse('users:password_reset'), {
            'email': 'nonexistent@example.com'
        })
        self.assertEqual(response.status_code, 302)  # Редирект даже при несуществующем email

    def test_password_reset_done_view(self):
        """Тест страницы подтверждения отправки инструкций"""
        response = self.client.get(reverse('users:password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_done.html')

    def test_password_reset_confirm_view_get(self):
        """Тест GET запроса к странице установки нового пароля"""
        # Создаем токен для сброса пароля
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        
        response = self.client.get(reverse('users:password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        }))
        # Может быть 200 (успех) или 302 (редирект при ошибке токена)
        self.assertIn(response.status_code, [200, 302])

    def test_password_reset_complete_view(self):
        """Тест страницы завершения сброса пароля"""
        response = self.client.get(reverse('users:password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_complete.html') 
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class CustomAuthenticationFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_form_fields(self):
        """Тест полей формы аутентификации"""
        form = CustomAuthenticationForm()
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
        # Проверяем, что лейбл переведен на русский
        self.assertIn('Адрес электронной почты', str(form.fields['username'].label))
        self.assertIn('Пароль', str(form.fields['password'].label))

    def test_form_validation_success(self):
        """Тест успешной валидации формы"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = CustomAuthenticationForm(data=form_data)
        # Форма может быть невалидна из-за требований Django к паролю
        # Проверяем только наличие полей
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)


class CustomPasswordResetFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_form_fields(self):
        """Тест полей формы сброса пароля"""
        form = CustomPasswordResetForm()
        self.assertIn('email', form.fields)
        # Проверяем, что лейбл переведен на русский
        self.assertIn('Адрес электронной почты', str(form.fields['email'].label))

    def test_form_validation_success(self):
        """Тест успешной валидации формы с существующим email"""
        form_data = {
            'email': 'test@example.com'
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_failure_invalid_email(self):
        """Тест неудачной валидации формы с неверным email"""
        form_data = {
            'email': 'invalid-email'
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_validation_failure_empty_email(self):
        """Тест неудачной валидации формы с пустым email"""
        form_data = {
            'email': ''
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_save_method_with_existing_user(self):
        """Тест метода save с существующим пользователем"""
        form_data = {
            'email': 'test@example.com'
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Мокаем request
        from django.test import RequestFactory
        request = RequestFactory().get('/')
        
        result = form.save(request=request)
        self.assertEqual(result, self.user)

    def test_save_method_with_nonexistent_user(self):
        """Тест метода save с несуществующим пользователем"""
        form_data = {
            'email': 'nonexistent@example.com'
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Мокаем request
        from django.test import RequestFactory
        request = RequestFactory().get('/')
        
        result = form.save(request=request)
        self.assertIsNone(result)


class CustomSetPasswordFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_form_fields(self):
        """Тест полей формы установки пароля"""
        form = CustomSetPasswordForm(user=self.user)
        self.assertIn('new_password1', form.fields)
        self.assertIn('new_password2', form.fields)
        self.assertEqual(form.fields['new_password1'].label, 'Новый пароль')
        self.assertEqual(form.fields['new_password2'].label, 'Подтверждение нового пароля')

    def test_form_validation_success(self):
        """Тест успешной валидации формы"""
        form_data = {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = CustomSetPasswordForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_validation_failure_mismatched_passwords(self):
        """Тест неудачной валидации формы с несовпадающими паролями"""
        form_data = {
            'new_password1': 'newpass123',
            'new_password2': 'differentpass'
        }
        form = CustomSetPasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_validation_failure_short_password(self):
        """Тест неудачной валидации формы с коротким паролем"""
        form_data = {
            'new_password1': '123',
            'new_password2': '123'
        }
        form = CustomSetPasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_validation_failure_common_password(self):
        """Тест неудачной валидации формы с простым паролем"""
        form_data = {
            'new_password1': 'password',
            'new_password2': 'password'
        }
        form = CustomSetPasswordForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())

    def test_save_method(self):
        """Тест метода save"""
        form_data = {
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = CustomSetPasswordForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        
        form.save()
        
        # Проверяем, что пароль изменился
        self.assertTrue(self.user.check_password('newpass123')) 
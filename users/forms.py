from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class CustomAuthenticationForm(AuthenticationForm):
    """
    Кастомная форма аутентификации
    """
    username = forms.CharField(
        label=_('Email'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class CustomPasswordResetForm(PasswordResetForm):
    """
    Форма для запроса сброса пароля
    """
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def save(self, domain_override=None,
             subject_template_name='users/password_reset_subject.txt',
             email_template_name='users/password_reset_email.html',
             use_https=False, token_generator=None,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Отправляет email с инструкциями по сбросу пароля
        """
        email = self.cleaned_data["email"]
        if not token_generator:
            token_generator = default_token_generator

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        # Отправляем email
        context = {
            'email': email,
            'domain': domain_override or request.get_host(),
            'site_name': 'Rehabs Platform',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
            'user': user,
            **(extra_email_context or {}),
        }
        
        self.send_mail(
            subject_template_name,
            email_template_name,
            context,
            from_email,
            email,
            html_email_template_name=html_email_template_name,
        )

        return user

class CustomSetPasswordForm(SetPasswordForm):
    """
    Форма для установки нового пароля
    """
    new_password1 = forms.CharField(
        label=_('Новый пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_('Подтверждение нового пароля'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    ) 
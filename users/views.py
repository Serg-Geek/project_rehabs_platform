from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import CustomPasswordResetForm, CustomSetPasswordForm, CustomAuthenticationForm
from django.contrib.auth import login

# Create your views here.

class CustomLoginView(LoginView):
    """
    Представление для входа в систему
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        """
        Обработка успешного входа
        """
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Вы успешно вошли в систему.')
        )
        return response


class CustomLogoutView(LogoutView):
    next_page = 'core:home'


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/profile.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        return self.request.user


class CustomPasswordResetView(PasswordResetView):
    """
    Представление для запроса сброса пароля
    """
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = '/users/password_reset/done/'

    def form_valid(self, form):
        """
        Обработка успешной отправки формы
        """
        email = form.cleaned_data['email']
        messages.success(
            self.request,
            _('Инструкции по сбросу пароля отправлены на ваш email.')
        )
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Представление для установки нового пароля
    """
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = '/users/reset/done/'

    def form_valid(self, form):
        """
        Обработка успешной установки нового пароля
        """
        user = form.user
        
        # Устанавливаем новый пароль
        form.save()
        
        # Автоматически входим пользователя
        login(self.request, user)
        
        messages.success(
            self.request,
            _('Ваш пароль успешно изменен.')
        )
        
        return super().form_valid(form)

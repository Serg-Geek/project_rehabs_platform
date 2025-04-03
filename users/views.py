from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


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

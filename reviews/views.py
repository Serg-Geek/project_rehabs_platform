from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import Review
from django.contrib.contenttypes.models import ContentType
from facilities.models import RehabCenter, Clinic
from django.http import Http404

# Create your views here.

class ReviewListView(ListView):
    """Список отзывов о специалисте"""
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        specialist_id = self.kwargs.get('specialist_id')
        return Review.objects.filter(
            specialist_id=specialist_id,
            is_published=True
        ).select_related('author')

class FacilityReviewCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание нового отзыва о медицинском учреждении"""
    model = Review
    template_name = 'reviews/review_form.html'
    fields = ['rating', 'text']
    success_message = 'Отзыв успешно добавлен'

    def form_valid(self, form):
        facility_type = self.kwargs['facility_type']
        facility_id = self.kwargs['facility_id']
        
        if facility_type == 'rehab':
            from facilities.models import RehabCenter
            model = RehabCenter
        elif facility_type == 'clinic':
            from facilities.models import Clinic
            model = Clinic
        else:
            raise Http404("Неверный тип учреждения")
            
        facility = get_object_or_404(model, id=facility_id)
        content_type = ContentType.objects.get_for_model(model)
        
        form.instance.content_type = content_type
        form.instance.object_id = facility_id
        form.instance.author = self.request.user
        
        return super().form_valid(form)

    def get_success_url(self):
        facility_type = self.kwargs.get('facility_type')
        facility_id = self.kwargs.get('facility_id')
        return reverse_lazy('facilities:detail', kwargs={
            'facility_type': facility_type,
            'pk': facility_id
        })

class ReviewCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание нового отзыва о специалисте"""
    model = Review
    template_name = 'reviews/review_form.html'
    fields = ['rating', 'text']
    success_message = 'Отзыв успешно добавлен'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.specialist_id = self.kwargs['specialist_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reviews:list', kwargs={'specialist_id': self.kwargs['specialist_id']})

class ReviewUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование отзыва"""
    model = Review
    template_name = 'reviews/review_form.html'
    fields = ['rating', 'text']
    success_message = 'Отзыв успешно обновлен'

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('reviews:list', kwargs={'specialist_id': self.object.specialist_id})

class ReviewDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Удаление отзыва"""
    model = Review
    success_message = 'Отзыв успешно удален'

    def get_queryset(self):
        return Review.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('reviews:list', kwargs={'specialist_id': self.object.specialist_id})

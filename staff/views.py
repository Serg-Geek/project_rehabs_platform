from django.shortcuts import render
from django.views.generic import DetailView
from .models import FacilitySpecialist

# Create your views here.

class SpecialistDetailView(DetailView):
    model = FacilitySpecialist
    template_name = 'staff/specialist_detail.html'
    context_object_name = 'specialist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specialist = context['specialist']
        return context

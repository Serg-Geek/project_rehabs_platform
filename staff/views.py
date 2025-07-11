from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.db.models import Q
from .models import FacilitySpecialist

# Create your views here.

class SpecialistsListView(ListView):
    model = FacilitySpecialist
    template_name = 'staff/specialists_list.html'
    context_object_name = 'specialists'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = FacilitySpecialist.objects.filter(is_active=True)
        
        # Поиск по имени или должности
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(position__icontains=search_query)
            )
        
        return queryset.order_by('last_name', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

class SpecialistDetailView(DetailView):
    model = FacilitySpecialist
    template_name = 'staff/specialist_detail.html'
    context_object_name = 'specialist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем документы специалиста в контекст
        context['documents'] = self.object.documents.filter(is_active=True)
        return context

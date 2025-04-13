from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import AnonymousRequest

# Create your views here.

class ConsultationRequestView(CreateView):
    model = AnonymousRequest
    fields = ['phone']  # Только телефон, остальное заполним в form_valid
    template_name = 'facilities/includes/consultation.html'
    success_url = reverse_lazy('requests:success')

    def form_valid(self, form):
        try:
            # Set default values
            form.instance.status = AnonymousRequest.Status.NEW
            form.instance.source = 'consultation_form'
            form.instance.request_type = AnonymousRequest.RequestType.CONSULTATION
            
            # Используем имя пользователя, если оно указано
            user_name = self.request.POST.get('name', '').strip()
            form.instance.name = user_name if user_name else 'Анонимный пользователь'
            
            form.instance.message = 'Заявка с формы консультации'  # Устанавливаем значение по умолчанию
            
            # Map service type to preferred_service
            service_type = self.request.POST.get('service-type')
            if service_type == 'consultation':
                form.instance.preferred_service = 'Консультация'
            elif service_type == 'therapy':
                form.instance.preferred_service = 'Терапия'
            elif service_type == 'support':
                form.instance.preferred_service = 'Поддержка'
            else:
                form.instance.preferred_service = 'Консультация'  # Значение по умолчанию
            
            # Сохраняем форму
            response = super().form_valid(form)
            
            # Проверяем, является ли запрос AJAX-запросом
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'request_number': form.instance.id,
                    'message': 'Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.'
                })
            
            # Если это не AJAX-запрос, перенаправляем на страницу успеха
            messages.success(self.request, 'Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.')
            return redirect('requests:success')
        except Exception as e:
            # Проверяем, является ли запрос AJAX-запросом
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Произошла ошибка при обработке заявки: {str(e)}'
                })
            
            # Если это не AJAX-запрос, перенаправляем на страницу ошибки
            messages.error(self.request, f'Произошла ошибка при обработке заявки: {str(e)}')
            return redirect('requests:error', error_message=str(e))

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f'Ошибка в поле {field}: {error}')
        
        # Проверяем, является ли запрос AJAX-запросом
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': '\n'.join(error_messages)
            })
        
        # Если это не AJAX-запрос, перенаправляем на страницу ошибки
        return redirect('requests:error', error_message='\n'.join(error_messages))

class PartnerRequestView(CreateView):
    model = AnonymousRequest
    fields = ['phone', 'name', 'organization', 'message']
    template_name = 'index.html'
    success_url = reverse_lazy('requests:success')

    def form_valid(self, form):
        try:
            # Set default values
            form.instance.status = AnonymousRequest.Status.NEW
            form.instance.source = 'partner_form'
            form.instance.request_type = AnonymousRequest.RequestType.PARTNER
            
            # Сохраняем форму
            response = super().form_valid(form)
            
            # Проверяем, является ли запрос AJAX-запросом
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'request_number': form.instance.id,
                    'message': 'Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.'
                })
            
            # Если это не AJAX-запрос, перенаправляем на страницу успеха
            messages.success(self.request, 'Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.')
            return redirect('requests:success')
        except Exception as e:
            # Проверяем, является ли запрос AJAX-запросом
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Произошла ошибка при обработке заявки: {str(e)}'
                })
            
            # Если это не AJAX-запрос, перенаправляем на страницу ошибки
            messages.error(self.request, f'Произошла ошибка при обработке заявки: {str(e)}')
            return redirect('requests:error', error_message=str(e))

    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f'Ошибка в поле {field}: {error}')
        
        # Проверяем, является ли запрос AJAX-запросом
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': '\n'.join(error_messages)
            })
        
        # Если это не AJAX-запрос, перенаправляем на страницу ошибки
        return redirect('requests:error', error_message='\n'.join(error_messages))

def success_view(request):
    return render(request, 'requests/success.html')

def error_view(request):
    error_message = request.GET.get('error_message', '')
    return render(request, 'requests/error.html', {'error_message': error_message})

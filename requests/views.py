from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import AnonymousRequest, Request, DependentRequest
from django.utils import timezone

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
            form.instance.source = AnonymousRequest.Source.WEBSITE_FORM
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
    fields = ['name', 'phone', 'email', 'message']
    template_name = 'index.html'
    success_url = reverse_lazy('requests:success')

    def form_valid(self, form):
        try:
            # Set default values
            form.instance.status = AnonymousRequest.Status.NEW
            form.instance.request_type = AnonymousRequest.RequestType.PARTNER
            form.instance.source = AnonymousRequest.Source.WEBSITE_FORM
            
            # Сохраняем форму
            response = super().form_valid(form)
            
            # Проверяем, является ли запрос AJAX-запросом
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Заявка успешно отправлена',
                    'request_number': form.instance.id
                })
            return response
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Произошла ошибка при отправке заявки'
                }, status=500)
            return super().form_invalid(form)

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

class DependentRequestView(CreateView):
    model = DependentRequest
    template_name = 'facilities/includes/consultation.html'
    fields = ['phone', 'addiction_type']
    success_url = reverse_lazy('requests:success')

    def form_valid(self, form):
        try:
            # Устанавливаем статус по умолчанию
            form.instance.status = DependentRequest.Status.NEW
            
            # Устанавливаем тип контакта как анонимный по умолчанию
            form.instance.contact_type = DependentRequest.ContactType.ANONYMOUS
            
            # Получаем имя, если оно указано
            user_name = self.request.POST.get('name', '').strip()
            if user_name:
                form.instance.first_name = user_name
            
            # Получаем тип сервиса
            service_type = self.request.POST.get('service-type')
            if service_type == 'consultation':
                form.instance.preferred_treatment = 'Консультация'
            elif service_type == 'therapy':
                form.instance.preferred_treatment = 'Терапия'
            elif service_type == 'support':
                form.instance.preferred_treatment = 'Поддержка'
            
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

def print_request_report(request, request_id):
    """
    Представление для генерации печатной версии отчета по заявке
    с дополнительной информацией и оптимизацией запросов
    """
    if not request.user.is_staff:
        return redirect('admin:login')
    
    try:
        # Определяем тип заявки
        request_type = request.GET.get('type', 'anonymous')
        
        if request_type == 'dependent':
            # Если это заявка от зависимого
            req = DependentRequest.objects.select_related('responsible_staff').get(pk=request_id)
            action_logs = []
        else:
            # По умолчанию - анонимная заявка с оптимизацией запросов
            req = AnonymousRequest.objects.select_related(
                'created_by', 
                'updated_by', 
                'assigned_to'
            ).get(pk=request_id)
            
            # Получаем логи действий только для анонимных заявок
            action_logs = req.action_logs.select_related('user').order_by('-created_at')[:10]
            
        # Общие данные для всех типов заявок
        notes = []
        status_history = []
        
        # Проверяем, есть ли у объекта заявки атрибут notes и загружаем с оптимизацией
        if hasattr(req, 'notes') and req.notes is not None:
            notes = req.notes.all().select_related('created_by').order_by('-created_at')
            
        # Проверяем, есть ли у объекта заявки атрибут status_history и загружаем с оптимизацией
        if hasattr(req, 'status_history') and req.status_history is not None:
            status_history = req.status_history.all().select_related('changed_by').order_by('-changed_at')
            
        # Формируем контекст с дополнительными данными
        context = {
            'request': req,
            'notes': notes,
            'status_history': status_history,
            'action_logs': action_logs,
            'user': request.user,
            'title': f'Отчет по заявке #{req.id}',
            'report_type': 'enhanced',
            'generation_time': timezone.now(),
        }
        
        # Проверяем наличие предпочтительного учреждения
        if hasattr(req, 'preferred_facility') and req.preferred_facility is not None:
            context['facility'] = req.preferred_facility
            
        # Добавляем статистику обработки для административных целей
        if request.user.is_superuser:
            # Если пользователь суперпользователь, добавляем статистику
            processing_time = None
            if req.status in ['completed', 'closed', 'treatment_completed']:
                # Вычисляем время обработки для закрытых заявок
                if hasattr(req, 'status_history') and req.status_history.exists():
                    first_status = req.status_history.order_by('changed_at').first()
                    last_status = req.status_history.order_by('-changed_at').first()
                    if first_status and last_status:
                        processing_time = last_status.changed_at - first_status.changed_at
            
            context['processing_time'] = processing_time
            
        return render(request, 'requests/print_report.html', context)
        
    except (AnonymousRequest.DoesNotExist, DependentRequest.DoesNotExist):
        messages.error(request, 'Заявка не найдена')
        return redirect('admin:index')

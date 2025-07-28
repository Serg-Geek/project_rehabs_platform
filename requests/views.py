from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import AnonymousRequest, DependentRequest
from django.utils import timezone
from facilities.models import Clinic, RehabCenter, PrivateDoctor, OrganizationType
from services.request_service import RequestService

# Create your views here.

class ConsultationRequestView(CreateView):
    """
    View for creating consultation requests.
    
    Uses RequestService for business logic processing.
    """
    model = AnonymousRequest
    fields = ['phone']  # Только телефон, остальное заполним в form_valid
    template_name = 'facilities/includes/consultation.html'
    success_url = reverse_lazy('requests:success')

    def __init__(self, *args, **kwargs):
        """
        Initialize the view with RequestService.
        
        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.request_service = RequestService()

    def form_valid(self, form):
        """
        Process valid form submission.
        
        Args:
            form: Valid form instance
            
        Returns:
            HttpResponse: JSON response for AJAX or redirect for regular requests
        """
        try:
            # Делегируем логику сервису
            result = self.request_service.create_consultation_request(
                form_data=form.cleaned_data,
                request_data=self.request.POST,
                user=self.request.user
            )
            
            if result.success:
                # Успешное создание
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'request_number': result.data.id,
                        'message': result.message
                    })
                else:
                    messages.success(self.request, result.message)
                    return redirect('requests:success')
            else:
                # Ошибка в сервисе
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': result.error
                    })
                else:
                    messages.error(self.request, result.error)
                    return redirect('requests:error')
                    
        except Exception as e:
            # Неожиданная ошибка
            error_message = f'Произошла ошибка при обработке заявки: {str(e)}'
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(self.request, error_message)
                return redirect('requests:error')

    def form_invalid(self, form):
        """
        Process invalid form submission.
        
        Args:
            form: Invalid form instance
            
        Returns:
            HttpResponse: JSON response for AJAX or redirect for regular requests
        """
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f'Ошибка в поле {field}: {error}')
        
        error_text = '\n'.join(error_messages)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': error_text
            })
        
        return redirect('requests:error', error_message=error_text)


class PartnerRequestView(CreateView):
    """
    View for creating partnership requests.
    
    Uses RequestService for business logic processing.
    """
    model = AnonymousRequest
    fields = ['name', 'phone', 'email', 'message']  # Используем существующие поля
    template_name = 'index.html'
    success_url = reverse_lazy('requests:success')

    def __init__(self, *args, **kwargs):
        """
        Initialize the view with RequestService.
        
        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.request_service = RequestService()

    def form_valid(self, form):
        """
        Process valid form submission.
        
        Args:
            form: Valid form instance
            
        Returns:
            HttpResponse: JSON response for AJAX or redirect for regular requests
        """
        try:
            # Делегируем логику сервису
            result = self.request_service.create_partner_request(
                form_data=form.cleaned_data,
                request_data=self.request.POST,
                user=self.request.user
            )
            
            if result.success:
                # Успешное создание
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'request_number': result.data.id,
                        'message': result.message
                    })
                else:
                    messages.success(self.request, result.message)
                    return redirect('requests:success')
            else:
                # Ошибка в сервисе
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': result.error
                    })
                else:
                    messages.error(self.request, result.error)
                    return redirect('requests:error')
                    
        except Exception as e:
            # Неожиданная ошибка
            error_message = f'Произошла ошибка при обработке заявки: {str(e)}'
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(self.request, error_message)
                return redirect('requests:error')

    def form_invalid(self, form):
        """
        Process invalid form submission.
        
        Args:
            form: Invalid form instance
            
        Returns:
            HttpResponse: JSON response for AJAX or redirect for regular requests
        """
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f'Ошибка в поле {field}: {error}')
        
        error_text = '\n'.join(error_messages)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': error_text
            })
        
        return redirect('requests:error', error_message=error_text)


class DependentRequestView(CreateView):
    """
    View for creating dependent treatment requests.
    
    Uses RequestService for business logic processing.
    """
    model = DependentRequest
    template_name = 'facilities/includes/consultation.html'
    fields = ['phone', 'addiction_type']  # Используем существующие поля
    success_url = reverse_lazy('requests:success')

    def __init__(self, *args, **kwargs):
        """
        Initialize the view with RequestService.
        
        Args:
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.request_service = RequestService()

    def form_valid(self, form):
        """
        Process valid form submission.
        
        Args:
            form: Valid form instance
            
        Returns:
            HttpResponse: JSON response for AJAX or redirect for regular requests
        """
        try:
            # Делегируем логику сервису
            result = self.request_service.create_dependent_request(
                form_data=form.cleaned_data,
                request_data=self.request.POST,
                user=self.request.user
            )
            
            if result.success:
                # Успешное создание
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'request_number': result.data.id,
                        'message': result.message
                    })
                else:
                    messages.success(self.request, result.message)
                    return redirect('requests:success')
            else:
                # Ошибка в сервисе
                if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': result.error
                    })
                else:
                    messages.error(self.request, result.error)
                    return redirect('requests:error')
                    
        except Exception as e:
            # Неожиданная ошибка
            error_message = f'Произошла ошибка при обработке заявки: {str(e)}'
            
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            else:
                messages.error(self.request, error_message)
                return redirect('requests:error')

    def form_invalid(self, form):
        """
        Process invalid form submission.
        
        Args:
            form: Invalid form instance
            
        Returns:
            HttpResponse: JSON response for AJAX or redirect for regular requests
        """
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f'Ошибка в поле {field}: {error}')
        
        error_text = '\n'.join(error_messages)
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': error_text
            })
        
        return redirect('requests:error', error_message=error_text)


def success_view(request):
    """
    View for successful request submission page.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered success page
    """
    return render(request, 'requests/success.html')


def error_view(request):
    """
    View for request submission error page.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered error page with error message
    """
    error_message = request.GET.get('error_message', 'Произошла неизвестная ошибка')
    return render(request, 'requests/error.html', {'error_message': error_message})


def print_request_report(request, request_id):
    """
    View for printing request report.
    
    Args:
        request: HTTP request object
        request_id: ID of the request to print
        
    Returns:
        HttpResponse: Rendered print report page or redirect on error
    """
    try:
        # Пытаемся найти заявку среди анонимных заявок
        try:
            request_obj = AnonymousRequest.objects.get(id=request_id)
            request_type = 'anonymous'
            
            # Получаем связанные данные для анонимной заявки
            from .models import RequestNote, RequestStatusHistory, RequestActionLog
            notes = RequestNote.objects.filter(request=request_obj).order_by('-created_at')
            status_history = RequestStatusHistory.objects.filter(request=request_obj).order_by('-changed_at')
            action_logs = RequestActionLog.objects.filter(request=request_obj).order_by('-created_at')
            
        except AnonymousRequest.DoesNotExist:
            # Если не найдена, ищем среди заявок на зависимых
            try:
                request_obj = DependentRequest.objects.get(id=request_id)
                request_type = 'dependent'
                
                # Получаем связанные данные для заявки зависимого
                from .models import DependentRequestNote, DependentRequestStatusHistory
                notes = DependentRequestNote.objects.filter(request=request_obj).order_by('-created_at')
                status_history = DependentRequestStatusHistory.objects.filter(request=request_obj).order_by('-changed_at')
                action_logs = []  # Для DependentRequest нет action_logs
                
            except DependentRequest.DoesNotExist:
                messages.error(request, 'Заявка не найдена')
                return redirect('requests:error')

        # Вычисляем время обработки
        processing_time = None
        if status_history.count() > 1:
            first_change = status_history.last()
            last_change = status_history.first()
            if first_change and last_change:
                processing_time = last_change.changed_at - first_change.changed_at

        context = {
            'request': request_obj,  # Используем 'request' для совместимости с шаблоном
            'request_type': request_type,
            'print_date': timezone.now(),
            'generation_time': timezone.now(),
            'user': request.user,
            'notes': notes,
            'status_history': status_history,
            'action_logs': action_logs,
            'processing_time': processing_time,
            'title': f'Отчет по заявке #{request_obj.id}',
            'report_type': 'enhanced' if request.user.is_superuser else 'standard'
        }
        
        return render(request, 'requests/print_report.html', context)
        
    except Exception as e:
        messages.error(request, f'Ошибка при формировании отчета: {str(e)}')
        return redirect('requests:error')


def get_organizations_by_type(request):
    """
    AJAX view for getting organizations by type.
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: JSON response with organizations or error
    """
    try:
        org_type = request.GET.get('type')
        
        if not org_type:
            return JsonResponse({
                'success': False,
                'error': 'Не указан тип организации'
            })
        
        # Используем сервис для получения организаций
        request_service = RequestService()
        result = request_service.get_organizations_by_type(org_type)
        
        if result.success:
            return JsonResponse({
                'success': True,
                'organizations': result.data
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        })

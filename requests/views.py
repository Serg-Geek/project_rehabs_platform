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
    Представление для создания заявки на консультацию.
    
    Использует RequestService для обработки бизнес-логики.
    """
    model = AnonymousRequest
    fields = ['phone']  # Только телефон, остальное заполним в form_valid
    template_name = 'facilities/includes/consultation.html'
    success_url = reverse_lazy('requests:success')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_service = RequestService()

    def form_valid(self, form):
        """Обработка валидной формы."""
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
        """Обработка невалидной формы."""
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
    Представление для создания заявки на партнерство.
    
    Использует RequestService для обработки бизнес-логики.
    """
    model = AnonymousRequest
    fields = ['name', 'phone', 'email', 'message']  # Используем существующие поля
    template_name = 'index.html'
    success_url = reverse_lazy('requests:success')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_service = RequestService()

    def form_valid(self, form):
        """Обработка валидной формы."""
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
        """Обработка невалидной формы."""
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
    Представление для создания заявки на лечение зависимого.
    
    Использует RequestService для обработки бизнес-логики.
    """
    model = DependentRequest
    template_name = 'facilities/includes/consultation.html'
    fields = ['phone', 'addiction_type']  # Используем существующие поля
    success_url = reverse_lazy('requests:success')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_service = RequestService()

    def form_valid(self, form):
        """Обработка валидной формы."""
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
        """Обработка невалидной формы."""
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
    """Представление для страницы успешной отправки заявки."""
    return render(request, 'requests/success.html')


def error_view(request):
    """Представление для страницы ошибки при отправке заявки."""
    error_message = request.GET.get('error_message', 'Произошла неизвестная ошибка')
    return render(request, 'requests/error.html', {'error_message': error_message})


def print_request_report(request, request_id):
    """Представление для печати отчета по заявке."""
    try:
        # Пытаемся найти заявку среди анонимных заявок
        try:
            request_obj = AnonymousRequest.objects.get(id=request_id)
            request_type = 'anonymous'
        except AnonymousRequest.DoesNotExist:
            # Если не найдена, ищем среди заявок на зависимых
            try:
                request_obj = DependentRequest.objects.get(id=request_id)
                request_type = 'dependent'
            except DependentRequest.DoesNotExist:
                messages.error(request, 'Заявка не найдена')
                return redirect('requests:error')

        context = {
            'request_obj': request_obj,
            'request_type': request_type,
            'print_date': timezone.now(),
        }
        
        return render(request, 'requests/print_report.html', context)
        
    except Exception as e:
        messages.error(request, f'Ошибка при формировании отчета: {str(e)}')
        return redirect('requests:error')


def get_organizations_by_type(request):
    """AJAX представление для получения организаций по типу."""
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
            'error': f'Ошибка получения организаций: {str(e)}'
        })

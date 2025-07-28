"""
Service for handling request-related business logic.

This service handles all business logic related to requests,
separating it from views and models.
"""

from typing import Dict, Any, Optional
from django.utils import timezone
from django.contrib.auth import get_user_model
from .base import BaseService
from .results import ServiceResult
from .email_service import EmailService
from requests.models import AnonymousRequest, DependentRequest
from facilities.models import Clinic, RehabCenter, PrivateDoctor
from core.logging import business_logger, error_logger

User = get_user_model()


class RequestService(BaseService):
    """
    Service for handling request operations.
    
    This service encapsulates all business logic related to creating,
    updating, and managing requests.
    """
    
    def __init__(self):
        super().__init__()
        self.email_service = EmailService()
    
    def create_consultation_request(self, form_data: Dict[str, Any], 
                                  request_data: Dict[str, Any], 
                                  user: Optional[User] = None) -> ServiceResult:
        """
        Create a consultation request.
        
        Args:
            form_data: Cleaned form data
            request_data: Raw request data
            user: Optional authenticated user
            
        Returns:
            ServiceResult: Result of the operation
        """
        try:
            # Validate required fields
            required_fields = ['phone']
            validation_result = self.validate_required_fields(form_data, required_fields)
            if not validation_result:
                return validation_result
            
            # Create request object
            request_obj = AnonymousRequest(
                name=self._get_user_name(request_data, user),
                phone=form_data['phone'],
                status=AnonymousRequest.Status.NEW,
                source=AnonymousRequest.Source.WEBSITE_FORM,
                request_type=AnonymousRequest.RequestType.CONSULTATION,
                message=self._get_default_message('consultation')
            )
            
            # Map service type to preferred service
            service_type = self.safe_get(request_data, 'service-type')
            request_obj.preferred_service = self._map_service_type(service_type)
            
            # Set priority based on service type
            request_obj.priority = self._determine_priority(service_type)
            
            # Save the request
            request_obj.save()
            
            # Логируем создание заявки
            business_logger.log_request_created(
                request_obj=request_obj,
                user=user,
                ip_address=getattr(self, 'request_ip', None)
            )
            
            # Отправляем email-уведомление администратору
            try:
                self.email_service.send_new_request_notification(request_obj)
            except Exception as email_error:
                # Логируем ошибку отправки email, но не прерываем основной процесс
                self.log_error(f"Failed to send email notification for request #{request_obj.id}", email_error)
            
            self.log_info("Consultation request created", 
                         request_id=request_obj.id,
                         service_type=service_type)
            
            return ServiceResult.success_result(
                data=request_obj,
                message="Заявка на консультацию успешно создана"
            )
            
        except Exception as e:
            # Логируем ошибку
            error_logger.log_exception(
                exception=e,
                context={
                    'method': 'create_consultation_request',
                    'service_type': self.safe_get(request_data, 'service-type'),
                    'user_id': user.id if user else None,
                },
                user=user
            )
            self.log_error("Error creating consultation request", e)
            return ServiceResult.error_result(
                error="Ошибка создания заявки на консультацию"
            )
    
    def create_partner_request(self, form_data: Dict[str, Any], 
                             request_data: Dict[str, Any], 
                             user: Optional[User] = None) -> ServiceResult:
        """
        Create a partnership request.
        
        Args:
            form_data: Cleaned form data
            request_data: Raw request data
            user: Optional authenticated user
            
        Returns:
            ServiceResult: Result of the operation
        """
        try:
            # Validate required fields
            required_fields = ['name', 'phone', 'email', 'message']
            validation_result = self.validate_required_fields(form_data, required_fields)
            if not validation_result:
                return validation_result
            
            # Create request object
            request_obj = AnonymousRequest(
                name=form_data['name'],
                phone=form_data['phone'],
                email=form_data['email'],
                message=form_data['message'],
                status=AnonymousRequest.Status.NEW,
                source=AnonymousRequest.Source.WEBSITE_FORM,
                request_type=AnonymousRequest.RequestType.PARTNER
            )
            
            # Save the request
            request_obj.save()
            
            # Логируем создание заявки
            business_logger.log_request_created(
                request_obj=request_obj,
                user=user,
                ip_address=getattr(self, 'request_ip', None)
            )
            
            # Отправляем email-уведомление администратору
            try:
                self.email_service.send_new_request_notification(request_obj)
            except Exception as email_error:
                # Логируем ошибку отправки email, но не прерываем основной процесс
                self.log_error(f"Failed to send email notification for request #{request_obj.id}", email_error)
            
            self.log_info("Partnership request created", 
                         request_id=request_obj.id)
            
            return ServiceResult.success_result(
                data=request_obj,
                message="Заявка на партнерство успешно создана"
            )
            
        except Exception as e:
            # Логируем ошибку
            error_logger.log_exception(
                exception=e,
                context="create_partner_request",
                user=user
            )
            
            return ServiceResult.error_result(
                error="Произошла ошибка при создании заявки на партнерство"
            )

    def create_dependent_request(self, form_data: Dict[str, Any], 
                               request_data: Dict[str, Any], 
                               user: Optional[User] = None) -> ServiceResult:
        """
        Create a dependent treatment request.
        
        Args:
            form_data: Cleaned form data
            request_data: Raw request data
            user: Optional authenticated user
            
        Returns:
            ServiceResult: Result of the operation
        """
        try:
            # Validate required fields
            required_fields = ['phone', 'addiction_type']
            validation_result = self.validate_required_fields(form_data, required_fields)
            if not validation_result:
                return validation_result
            
            # Create request object
            request_obj = DependentRequest(
                phone=form_data['phone'],
                addiction_type=form_data['addiction_type'],
                status=DependentRequest.Status.NEW,
                contact_type=DependentRequest.ContactType.ANONYMOUS
            )
            
            # Set additional fields from request data
            request_obj.first_name = self.safe_get(request_data, 'first_name')
            request_obj.last_name = self.safe_get(request_data, 'last_name')
            request_obj.email = self.safe_get(request_data, 'email')
            request_obj.age = self.safe_get_int(request_data, 'age')
            request_obj.addiction_duration = self.safe_get(request_data, 'addiction_duration')
            request_obj.current_condition = self.safe_get(request_data, 'current_condition')
            request_obj.preferred_treatment = self.safe_get(request_data, 'preferred_treatment')
            
            # Save the request
            request_obj.save()
            
            # Логируем создание заявки
            business_logger.log_request_created(
                request_obj=request_obj,
                user=user,
                ip_address=getattr(self, 'request_ip', None)
            )
            
            # Отправляем email-уведомление администратору
            try:
                self.email_service.send_new_dependent_request_notification(request_obj)
            except Exception as email_error:
                # Логируем ошибку отправки email, но не прерываем основной процесс
                self.log_error(f"Failed to send email notification for dependent request #{request_obj.id}", email_error)
            
            self.log_info("Dependent request created", 
                         request_id=request_obj.id,
                         addiction_type=form_data['addiction_type'])
            
            return ServiceResult.success_result(
                data=request_obj,
                message="Заявка на лечение зависимого успешно создана"
            )
            
        except Exception as e:
            # Логируем ошибку
            error_logger.log_exception(
                exception=e,
                context="create_dependent_request",
                user=user
            )
            
            return ServiceResult.error_result(
                error="Произошла ошибка при создании заявки на лечение зависимого"
            )

    def get_organizations_by_type(self, org_type: str) -> ServiceResult:
        """
        Get organizations by type for AJAX requests.
        
        Args:
            org_type: Type of organization to retrieve
            
        Returns:
            ServiceResult: Result with organizations data
        """
        try:
            if org_type == 'clinic':
                organizations = Clinic.objects.filter(is_active=True).values('id', 'name', 'city__name')
            elif org_type == 'rehab':
                organizations = RehabCenter.objects.filter(is_active=True).values('id', 'name', 'city__name')
            elif org_type == 'doctor':
                organizations = PrivateDoctor.objects.filter(is_active=True).values('id', 'name', 'city__name')
            else:
                return ServiceResult.error_result(
                    error="Неизвестный тип организации"
                )
            
            # Convert to list for JSON serialization
            org_list = list(organizations)
            
            self.log_info("Organizations retrieved by type", 
                         org_type=org_type,
                         count=len(org_list))
            
            return ServiceResult.success_result(
                data=org_list,
                message="Организации успешно получены"
            )
            
        except Exception as e:
            # Логируем ошибку
            error_logger.log_exception(
                exception=e,
                context="get_organizations_by_type",
                org_type=org_type
            )
            
            return ServiceResult.error_result(
                error="Произошла ошибка при получении организаций"
            )

    def _get_user_name(self, request_data: Dict[str, Any], user: Optional[User]) -> str:
        """
        Get user name from request data or user object.
        
        Args:
            request_data: Raw request data
            user: Optional authenticated user
            
        Returns:
            str: User name
        """
        if user and user.is_authenticated:
            return user.get_full_name() or user.username
        return self.safe_get(request_data, 'name', '')

    def _get_default_message(self, request_type: str) -> str:
        """
        Get default message for request type.
        
        Args:
            request_type: Type of request
            
        Returns:
            str: Default message
        """
        messages = {
            'consultation': 'Заявка на консультацию',
            'treatment': 'Заявка на лечение',
            'rehabilitation': 'Заявка на реабилитацию',
            'partner': 'Заявка на партнерство'
        }
        return messages.get(request_type, 'Заявка')

    def _map_service_type(self, service_type: Optional[str]) -> str:
        """
        Map service type to preferred service name.
        
        Args:
            service_type: Service type from form
            
        Returns:
            str: Mapped service name
        """
        service_mapping = {
            'alcohol': 'Лечение алкоголизма',
            'drugs': 'Лечение наркомании',
            'gambling': 'Лечение игромании',
            'rehabilitation': 'Реабилитация',
            'consultation': 'Консультация'
        }
        return service_mapping.get(service_type, 'Консультация')

    def _determine_priority(self, service_type: Optional[str]) -> str:
        """
        Determine request priority based on service type.
        
        Args:
            service_type: Service type from form
            
        Returns:
            str: Priority level
        """
        high_priority_types = ['alcohol', 'drugs']
        if service_type in high_priority_types:
            return AnonymousRequest.Priority.HIGH
        return AnonymousRequest.Priority.MEDIUM 
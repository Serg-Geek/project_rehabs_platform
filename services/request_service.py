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
from requests.models import AnonymousRequest, DependentRequest
from facilities.models import Clinic, RehabCenter, PrivateDoctor

User = get_user_model()


class RequestService(BaseService):
    """
    Service for handling request operations.
    
    This service encapsulates all business logic related to creating,
    updating, and managing requests.
    """
    
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
            
            self.log_info("Consultation request created", 
                         request_id=request_obj.id,
                         service_type=service_type)
            
            return ServiceResult.success_result(
                data=request_obj,
                message="Заявка на консультацию успешно создана"
            )
            
        except Exception as e:
            self.log_error("Error creating consultation request", e)
            return ServiceResult.error_result(
                error="Ошибка создания заявки на консультацию"
            )
    
    def create_partner_request(self, form_data: Dict[str, Any], 
                             request_data: Dict[str, Any], 
                             user: Optional[User] = None) -> ServiceResult:
        """
        Create a partner request.
        
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
                request_type=AnonymousRequest.RequestType.PARTNER,
                priority=AnonymousRequest.Priority.MEDIUM
            )
            
            # Save the request
            request_obj.save()
            
            self.log_info("Partner request created", 
                         request_id=request_obj.id,
                         name=form_data['name'])
            
            return ServiceResult.success_result(
                data=request_obj,
                message="Заявка на партнерство успешно создана"
            )
            
        except Exception as e:
            self.log_error("Error creating partner request", e)
            return ServiceResult.error_result(
                error="Ошибка создания заявки на партнерство"
            )
    
    def create_dependent_request(self, form_data: Dict[str, Any], 
                               request_data: Dict[str, Any], 
                               user: Optional[User] = None) -> ServiceResult:
        """
        Create a dependent request.
        
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
            
            # Create dependent request object
            request_obj = DependentRequest(
                phone=form_data['phone'],
                addiction_type=form_data['addiction_type'],
                status=DependentRequest.Status.NEW,
                contact_type=DependentRequest.ContactType.ANONYMOUS
            )
            
            # Set additional fields from request data
            request_obj.first_name = self.safe_get(request_data, 'name', '')
            request_obj.current_condition = self.safe_get(request_data, 'problem_description', '')
            request_obj.preferred_treatment = self._map_service_type(self.safe_get(request_data, 'service-type'))
            
            # Save the request
            request_obj.save()
            
            self.log_info("Dependent request created", 
                         request_id=request_obj.id,
                         addiction_type=form_data['addiction_type'])
            
            return ServiceResult.success_result(
                data=request_obj,
                message="Заявка на лечение зависимого успешно создана"
            )
            
        except Exception as e:
            self.log_error("Error creating dependent request", e)
            return ServiceResult.error_result(
                error="Ошибка создания заявки на лечение зависимого"
            )
    
    def get_organizations_by_type(self, org_type: str) -> ServiceResult:
        """
        Get organizations by type for AJAX requests.
        
        Args:
            org_type: Type of organization ('clinic', 'rehab', 'doctor')
            
        Returns:
            ServiceResult: List of organizations
        """
        try:
            organizations = []
            
            if org_type == 'clinic':
                organizations = Clinic.objects.filter(is_active=True).values('id', 'name')
            elif org_type == 'rehab':
                organizations = RehabCenter.objects.filter(is_active=True).values('id', 'name')
            elif org_type == 'doctor':
                organizations = PrivateDoctor.objects.filter(is_active=True).values('id', 'name')
            else:
                return ServiceResult.error_result(
                    error="Неверный тип организации",
                    code="INVALID_ORG_TYPE"
                )
            
            return ServiceResult.success_result(
                data=list(organizations),
                message=f"Найдено {len(organizations)} организаций"
            )
            
        except Exception as e:
            self.log_error("Error getting organizations by type", e, org_type=org_type)
            return ServiceResult.error_result(
                error="Ошибка получения списка организаций"
            )
    
    def _get_user_name(self, request_data: Dict[str, Any], user: Optional[User]) -> str:
        """Get user name from request data or user object."""
        name = self.safe_get(request_data, 'name', '').strip()
        if name:
            return name
        elif user and user.is_authenticated:
            return user.get_full_name() or user.username
        else:
            return 'Анонимный пользователь'
    
    def _get_default_message(self, request_type: str) -> str:
        """Get default message for request type."""
        messages = {
            'consultation': 'Заявка с формы консультации',
            'treatment': 'Заявка на лечение',
            'rehabilitation': 'Заявка на реабилитацию',
            'partner': 'Заявка на партнерство',
            'other': 'Заявка с сайта'
        }
        return messages.get(request_type, 'Заявка с сайта')
    
    def _map_service_type(self, service_type: Optional[str]) -> str:
        """Map service type to preferred service."""
        mapping = {
            'consultation': 'Консультация',
            'therapy': 'Терапия',
            'support': 'Поддержка',
            'alcoholism': 'Лечение алкоголизма',
            'drug_addiction': 'Лечение наркомании',
            'gambling': 'Лечение игровой зависимости',
            'other': 'Другие услуги'
        }
        return mapping.get(service_type, 'Консультация')
    
    def _determine_priority(self, service_type: Optional[str]) -> str:
        """Determine priority based on service type."""
        high_priority_types = ['alcoholism', 'drug_addiction']
        if service_type in high_priority_types:
            return AnonymousRequest.Priority.HIGH
        return AnonymousRequest.Priority.MEDIUM 
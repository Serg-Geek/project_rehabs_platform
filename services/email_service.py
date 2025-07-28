from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from typing import Optional, List
from requests.models import AnonymousRequest
import logging

logger = logging.getLogger('business')

class EmailService:
    """
    Service for sending email notifications to administrators.
    """
    
    def __init__(self):
        """
        Initialize the email service with configuration.
        """
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@rehabs-platform.com')
        self.admin_emails = getattr(settings, 'ADMIN_EMAILS', ['admin@rehabs-platform.com'])
    
    def send_new_request_notification(self, request_obj: AnonymousRequest) -> bool:
        """
        Send notification to administrator about new request.
        
        Args:
            request_obj: Request object
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = f'Новая заявка #{request_obj.id} - {request_obj.get_request_type_display()}'
            
            # Рендерим HTML и текстовый контент
            html_content = render_to_string('emails/new_request_admin.html', {
                'request': request_obj,
                'site_name': 'Центр помощи зависимым',
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
            })
            
            text_content = render_to_string('emails/new_request_admin.txt', {
                'request': request_obj,
                'site_name': 'Центр помощи зависимым',
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
            })
            
            # Отправляем email
            send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=self.admin_emails,
                html_message=html_content,
                fail_silently=False
            )
            
            # Логируем успешную отправку
            logger.info(
                f"Admin notification sent for request #{request_obj.id}",
                extra={
                    'request_id': request_obj.id,
                    'request_type': request_obj.request_type,
                    'recipients': self.admin_emails
                }
            )
            
            return True
            
        except Exception as e:
            # Логируем ошибку
            logger.error(
                f"Failed to send admin notification for request #{request_obj.id}: {str(e)}",
                extra={
                    'request_id': request_obj.id,
                    'error': str(e)
                }
            )
            return False
    
    def send_partner_request_notification(self, request_obj: AnonymousRequest) -> bool:
        """
        Send notification about partnership request.
        
        Args:
            request_obj: Partnership request object
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            subject = f'Новая заявка на партнерство #{request_obj.id}'
            
            # Рендерим HTML и текстовый контент
            html_content = render_to_string('emails/partner_request.html', {
                'request': request_obj,
                'site_name': 'Центр помощи зависимым',
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
            })
            
            text_content = render_to_string('emails/partner_request.txt', {
                'request': request_obj,
                'site_name': 'Центр помощи зависимым',
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000')
            })
            
            # Отправляем email
            send_mail(
                subject=subject,
                message=text_content,
                from_email=self.from_email,
                recipient_list=self.admin_emails,
                html_message=html_content,
                fail_silently=False
            )
            
            # Логируем успешную отправку
            logger.info(
                f"Partner request notification sent for request #{request_obj.id}",
                extra={
                    'request_id': request_obj.id,
                    'recipients': self.admin_emails
                }
            )
            
            return True
            
        except Exception as e:
            # Логируем ошибку
            logger.error(
                f"Failed to send partner request notification for request #{request_obj.id}: {str(e)}",
                extra={
                    'request_id': request_obj.id,
                    'error': str(e)
                }
            )
            return False 
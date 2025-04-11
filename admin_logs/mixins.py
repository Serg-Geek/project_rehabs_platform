from django.core.exceptions import PermissionDenied
from django.utils import timezone
from functools import wraps

class AccessControlMixin:
    def has_app_access(self, app_label, action):
        if self.request.user.is_superuser:
            return True
        
        return self.request.user.user_accesses.filter(
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_until__gte=timezone.now(),
            access_level__app_permissions__app_label=app_label,
            **{f'access_level__app_permissions__can_{action}': True}
        ).exists()

class ContentAdminMixin(AccessControlMixin):
    def has_content_access(self, action):
        return self.has_app_access(['blog', 'recovery_stories'], action)

    def can_manage_requests(self):
        """Проверка прав на управление заявками (для ContentAdmin)"""
        return self.has_app_access('requests', 'assign_responsible') or \
               self.has_app_access('requests', 'change_status')

class RequestsAdminMixin(AccessControlMixin):
    def has_requests_access(self, action):
        """Проверка прав на работу с заявками (для RequestsAdmin)"""
        if action == 'delete' or action == 'assign_responsible':
            return False
        return self.has_app_access('requests', action)

def require_app_access(app_label, action):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_app_access(app_label, action):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def require_content_access(action):
    return require_app_access(['blog', 'recovery_stories'], action)

def require_requests_access(action):
    return require_app_access('requests', action) 
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdminLogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_logs'
    verbose_name = _('Логи администраторов')

    def ready(self):
        import admin_logs.signals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FacilitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'facilities'
    verbose_name = _('Учреждения')

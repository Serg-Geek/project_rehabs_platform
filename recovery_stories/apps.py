from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RecoveryStoriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recovery_stories'
    verbose_name = _('Истории выздоровления')

    def ready(self):
        import recovery_stories.signals

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = _('User Accounts')
    label = 'accounts'  # Explicitly set the app label
    
    def ready(self):
        # Import signals to register them
        import accounts.signals

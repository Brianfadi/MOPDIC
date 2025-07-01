from django.apps import AppConfig
import warnings


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core'
    
    def ready(self):
        # Warn about deprecated models
        warnings.warn(
            "The models in the 'core' app are deprecated. "
            "Please use the models in the 'dashboard' app instead.",
            DeprecationWarning,
            stacklevel=2
        )

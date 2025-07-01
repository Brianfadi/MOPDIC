from django.apps import AppConfig


class CustomadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customadmin'
    verbose_name = 'MOPDIC Admin'
    
    def ready(self):
        # Import signals or other initialization code here
        import customadmin.signals

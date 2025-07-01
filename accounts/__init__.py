from django.contrib.auth import get_user_model as django_get_user_model

# This will be resolved when Django is fully loaded
def get_user_model():
    return django_get_user_model()

# Don't call get_user_model() at module level to avoid AppRegistryNotReady
__all__ = ['get_user_model']
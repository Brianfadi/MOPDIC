from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Activity
from .utils import log_activity

User = get_user_model()

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    """Log object creation and updates"""
    # Skip if this is a proxy model, Activity model, or not a model we want to track
    if (hasattr(instance, '_meta') and 
        not instance._meta.proxy and 
        not isinstance(instance, Activity)):  # Skip Activity model to prevent recursion
        action = 'create' if created else 'update'
        # Get the request from thread local storage if available
        from crum import get_current_request
        request = get_current_request()
        
        if request:
            log_activity(
                request=request,
                action=action,
                instance=instance
            )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log object deletions"""
    # Skip if this is a proxy model, Activity model, or not a model we want to track
    if (hasattr(instance, '_meta') and 
        not instance._meta.proxy and 
        not isinstance(instance, Activity)):  # Skip Activity model to prevent recursion
        from crum import get_current_request
        request = get_current_request()
        
        if request:
            log_activity(
                request=request,
                action='delete',
                instance=instance
            )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user logins"""
    log_activity(
        request=request,
        action='login',
        instance=user
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logouts"""
    log_activity(
        request=request,
        action='logout',
        instance=user
    )

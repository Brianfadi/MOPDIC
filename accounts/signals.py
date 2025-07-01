from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.utils import timezone
from .models import UserActivity

User = get_user_model()

@receiver(post_save, sender=User)
def set_default_user_group(sender, instance, created, **kwargs):
    """
    Assign new users to the 'Viewer' group by default if no group is assigned.
    """
    if created and not instance.is_superuser and not instance.groups.exists():
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')
        instance.groups.add(viewer_group)
        instance.save()

@receiver(pre_save, sender=User)
def update_user_cache(sender, instance, **kwargs):
    """
    Clear the user's cache when their profile is updated.
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.last_login != instance.last_login:
                cache_key = f'user_{instance.id}_last_activity'
                cache.delete(cache_key)
        except User.DoesNotExist:
            pass  # New user, nothing to update

@receiver(post_delete, sender=User)
def delete_user_cache(sender, instance, **kwargs):
    """
    Clear the user's cache when their account is deleted.
    """
    cache_key = f'user_{instance.id}_last_activity'
    cache.delete(cache_key)

@receiver(m2m_changed, sender=User.groups.through)
def user_groups_changed(sender, instance, action, **kwargs):
    """
    Clear permission cache when user's groups change.
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        cache.delete(f'user_{instance.id}_permissions')

@receiver(post_save, sender=User)
def log_user_activity(sender, instance, created, **kwargs):
    """
    Log user activity when they log in or update their profile.
    """
    if created:
        action = 'Account created'
    else:
        action = 'Profile updated'
    
    # Get the request object if available
    request = None
    for frame in __import__('inspect').stack():
        if 'request' in frame[0].f_locals and hasattr(frame[0].f_locals['request'], 'user'):
            request = frame[0].f_locals['request']
            break
    
    # Log the activity
    UserActivity.objects.create(
        user=instance,
        action=action,
        ip_address=request.META.get('REMOTE_ADDR') if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT') if request else ''
    )

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache

User = get_user_model()

@receiver(post_save, sender=User)
def set_default_user_group(sender, instance, created, **kwargs):
    """
    Assign new users to the 'Viewer' group by default if no group is assigned.
    """
    if created and not instance.is_superuser:
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')
        instance.groups.add(viewer_group)
        instance.save()

@receiver(pre_save, sender=User)
def update_user_cache(sender, instance, **kwargs):
    """
    Clear the user's cache when their profile is updated.
    """
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

# Add any additional signal handlers below

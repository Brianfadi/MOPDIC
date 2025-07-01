from ipware import get_client_ip
from django.contrib.contenttypes.models import ContentType
from .models import Activity

def log_activity(request, action, instance=None, changes=None, **kwargs):
    """
    Log user activity
    
    Args:
        request: The request object
        action: The action performed (e.g., 'create', 'update', 'delete')
        instance: The model instance being acted upon (optional)
        changes: A dictionary of changes made (for updates)
        **kwargs: Additional fields to save with the activity
    """
    user = request.user if request.user.is_authenticated else None
    
    # Get client IP and user agent
    ip_address, _ = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Prepare activity data
    activity_data = {
        'user': user,
        'action': action,
        'ip_address': ip_address,
        'user_agent': user_agent,
        **kwargs
    }
    
    # Add instance information if provided
    if instance is not None:
        content_type = ContentType.objects.get_for_model(instance)
        activity_data.update({
            'content_type': content_type.model,
            'object_id': instance.pk,
            'object_repr': str(instance)[:200]  # Truncate to fit in the field
        })
    
    # Add changes if provided
    if changes and isinstance(changes, dict):
        changes_text = []
        for field, (old_value, new_value) in changes.items():
            changes_text.append(f"{field}: {old_value} → {new_value}")
        activity_data['changes'] = '\n'.join(changes_text)
    
    # Create the activity log
    Activity.objects.create(**activity_data)

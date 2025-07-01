from django import get_version

def admin_context(request):
    """
    Add common context variables to all admin templates.
    """
    return {
        'django_version': get_version(),
    }

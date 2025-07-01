from django.conf import settings

def auth_context(request):
    """
    Add user and permission information to the template context.
    """
    context = {}
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
        context.update({
            'current_user': user,
            'is_admin': user.is_superuser or user.groups.filter(name='Administrators').exists(),
            'is_editor': user.groups.filter(name='Editors').exists(),
            'is_viewer': user.groups.filter(name='Viewers').exists(),
        })
    
    return context

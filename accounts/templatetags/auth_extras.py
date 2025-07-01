from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from .. import get_user_model

register = template.Library()

def get_user_model_lazy():
    """Lazy loading of the User model to avoid circular imports."""
    return get_user_model()

@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user belongs to a specific group."""
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter(name='has_permission')
def has_permission(user, permission_codename):
    """Check if user has a specific permission."""
    if not user or not user.is_authenticated:
        return False
    return user.has_perm(permission_codename)

@register.filter(name='has_any_permission')
def has_any_permission(user, permission_codenames):
    """Check if user has any of the specified permissions."""
    if not user.is_authenticated:
        return False
    if isinstance(permission_codenames, str):
        permission_codenames = [p.strip() for p in permission_codenames.split(',')]
    return any(user.has_perm(perm) for perm in permission_codenames)

@register.filter(name='has_all_permissions')
def has_all_permissions(user, permission_codenames):
    """Check if user has all of the specified permissions."""
    if not user.is_authenticated:
        return False
    if isinstance(permission_codenames, str):
        permission_codenames = [p.strip() for p in permission_codenames.split(',')]
    return all(user.has_perm(perm) for perm in permission_codenames)

@register.simple_tag(takes_context=True)
def get_user_menu(context, user):
    """
    Template tag to get the user menu items.
    Usage: {% get_user_menu user as user_menu %}
    """
    if not user or not user.is_authenticated:
        return []
        
    # Build the user change URL manually since we're using a custom admin site
    user_change_url = f'/admin/accounts/user/{user.id}/change/'
    
    menu_items = [
        {
            'title': 'Profile',
            'url': user_change_url,
            'new_window': False
        },
        {
            'title': 'Change password',
            'url': '/admin/password_change/',
            'new_window': False
        },
        {
            'title': 'Log out',
            'url': '/admin/logout/',
            'new_window': False
        },
    ]
    
    # Add any custom menu items from settings if they exist
    custom_menu = getattr(settings, 'ADMIN_USER_MENU', [])
    if custom_menu and callable(custom_menu):
        menu_items = custom_menu(user, menu_items)
    
    return menu_items

@register.simple_tag(takes_context=True)
def if_has_perm(context, permission_codename, **kwargs):
    """
    Template tag to conditionally render content based on permission.
    Usage: {% if_has_perm 'app_label.permission_codename' %}
           Content to show if user has permission
           {% endif_has_perm %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return ''
    
    if request.user.has_perm(permission_codename):
        return kwargs.get('content', '')
    return ''

@register.inclusion_tag('admin/partials/permission_badge.html')
def permission_badge(user, size='md'):
    """Render a badge showing the user's highest role."""
    if not user or not user.is_authenticated:
        role = 'Guest'
        css_class = 'secondary'
    elif user.is_superuser:
        role = 'Super Admin'
        css_class = 'danger'
    elif get_user_model_lazy().objects.filter(groups__name='Administrators', pk=user.pk).exists():
        role = 'Administrator'
        css_class = 'primary'
    elif get_user_model_lazy().objects.filter(groups__name='Editors', pk=user.pk).exists():
        role = 'Editor'
        css_class = 'success'
    elif get_user_model_lazy().objects.filter(groups__name='Viewers', pk=user.pk).exists():
        role = 'Viewer'
        css_class = 'info'
    else:
        role = 'User'
        css_class = 'secondary'
    
    return {
        'role': role,
        'css_class': css_class,
        'size': size,
    }

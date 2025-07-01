import time
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache
from .models import User, UserActivity

class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity and update last activity timestamp.
    Also logs user actions to the UserActivity model.
    """
    
    def process_request(self, request):
        # Skip tracking for non-authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
            
        # Skip tracking for static/media files and admin URLs
        path = request.path_info.lstrip('/')
        if any(path.startswith(prefix) for prefix in settings.STATIC_URL) or \
           any(path.startswith(prefix) for prefix in settings.MEDIA_URL) or \
           path.startswith('admin/'):
            return None
            
        # Update last activity in cache
        cache_key = f'user_{request.user.id}_last_activity'
        last_activity = cache.get(cache_key)
        
        # Only update the database at most once per minute
        if last_activity is None or (timezone.now() - last_activity).total_seconds() > 60:
            # Update the user's last_activity field
            User.objects.filter(pk=request.user.id).update(last_activity=timezone.now())
            
            # Log the activity if it's a significant action
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                action = f"{request.method} {request.path}"
                UserActivity.objects.create(
                    user=request.user,
                    action=action,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
        
        # Always update the cache
        cache.set(cache_key, timezone.now(), settings.SESSION_COOKIE_AGE)
        
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

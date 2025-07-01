"""
URL configuration for mopdic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.views import LogoutView, LoginView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

def admin_logout(request):
    """Custom admin logout view that handles both GET and POST requests."""
    logout(request)
    return HttpResponseRedirect(reverse('main:login'))

# Disable admin site access unless in DEBUG mode
admin.site.site_header = "MOPDIC Administration"
admin.site.site_title = "MOPDIC Admin"
admin.site.index_title = "Welcome to MOPDIC Administration"

# Disable admin site access in production
if not settings.DEBUG:
    admin.site.login = lambda *args, **kwargs: HttpResponseForbidden()
    admin.site.logout = lambda *args, **kwargs: HttpResponseForbidden()

urlpatterns = [
    # Main app URLs
    path('', include('main.urls', namespace='main')),
    
    # Media files in production (served by WhiteNoise in production)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
    
    # Authentication URLs
    path('accounts/', include('django.contrib.auth.urls')),  # This includes login, password_reset, etc.
    
    # Custom admin URLs - This will handle all /admin/ URLs through our custom admin
    path('admin/', include('customadmin.urls', namespace='admin')),
    
    # JavaScript i18n for admin
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    
    # Logout
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]

# CKEditor URLs
urlpatterns += [
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

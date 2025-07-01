from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.forms import (
    AdminPasswordChangeForm, UserChangeForm, UserCreationForm,
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from .models import UserActivity
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.

class CustomAdminSite(admin.AdminSite):
    """Custom admin site with overridden functionality."""
    site_header = _('MOPDIC Administration')
    site_title = _('MOPDIC Admin')
    index_title = _('Dashboard')
    logout_template = 'admin/logout.html'
    login_template = 'admin/login.html'
    
    def __init__(self, name='admin'):
        super().__init__(name)
        self._registry = {}
        self.name = name
        
    def get_urls(self):
        from django.urls import path
        from django.contrib.auth.views import LogoutView
        
        # Get the default admin URLs
        urls = super().get_urls()
        
        # Add custom URLs
        custom_urls = [
            path(
                'logout/',
                self.logout,
                name='logout'
            ),
        ]
        
        # Add custom URLs before the default ones
        return custom_urls + urls
        
    def logout(self, request, extra_context=None):
        """
        Override the default logout view to use our custom template.
        """
        from django.contrib.auth import logout
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        logout(request)
        return HttpResponseRedirect(reverse('admin:login'))
    
    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return request.user.is_active and (request.user.is_staff or request.user.is_superuser)
    
    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for *every*
        page in the admin site.
        """
        context = super().each_context(request)
        # Add custom context variables
        context.update({
            'site_url': '/',
            'site_title': self.site_title,
            'site_header': self.site_header,
            'has_permission': self.has_permission(request),
            'available_apps': self.get_app_list(request) if self.has_permission(request) else [],
            'is_popup': False,
            'is_nav_sidebar_enabled': False,
        })
        return context
        
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            **(extra_context or {}),
        }
        
        # Add custom context for the dashboard
        if request.user.is_authenticated:
            # Get recent user activities
            recent_activities = UserActivity.objects.select_related('user') \
                .order_by('-timestamp')[:10]
            
            # Get user statistics
            user_count = get_user_model().objects.count()
            staff_count = get_user_model().objects.filter(is_staff=True).count()
            active_users = get_user_model().objects.filter(is_active=True).count()
            
            context.update({
                'recent_activities': recent_activities,
                'user_count': user_count,
                'staff_count': staff_count,
                'active_users': active_users,
            })
        
        request.current_app = self.name
        
        return TemplateResponse(
            request, self.index_template or 'admin/index.html', context
        )
    
    def app_index(self, request, app_label, extra_context=None):
        """
        Display the main app index page for the given app.
        """
        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        
        # Check if the user has any permissions for the models in this app
        if not any(app_dict['models']):
            raise PermissionDenied
        
        context = {
            **self.each_context(request),
            'title': _('%(app)s administration') % {'app': app_dict['name']},
            'app_list': [app_dict],
            'app_label': app_label,
            **(extra_context or {}),
        }
        
        request.current_app = self.name
        
        return TemplateResponse(
            request,
            self.app_index_template or [
                f"admin/{app_label}/app_index.html",
                'admin/app_index.html'
            ],
            context,
        )
    
    def get_urls(self):
        """Add our custom URLs to the admin site."""
        from django.urls import path
        
        urls = super().get_urls()
        
        # Add custom URLs here if needed
        custom_urls = [
            # Example:
            # path('my-custom-view/', self.admin_view(MyCustomView.as_view()), name='my-custom-view'),
        ]
        
        return custom_urls + urls
    
    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request, app_label)
        
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        
        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])
        
        return app_list

# Create an instance of our custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register the User model with our custom admin site
class UserAdmin(BaseUserAdmin):
    # Use our custom forms
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # The fields to be used in displaying the User model.
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Register the models with our custom admin site
custom_admin_site.register(get_user_model(), UserAdmin)

# Register other models
custom_admin_site.register(Group)
# custom_admin_site.register(Permission)  # Usually not needed as it's registered by default

# You can also register other models here if needed
# from .models import YourModel
# custom_admin_site.register(YourModel)

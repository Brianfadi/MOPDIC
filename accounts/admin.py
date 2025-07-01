from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AdminPasswordChangeForm

from .models import User, UserActivity
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm, ProfileUpdateForm


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = CustomPasswordChangeForm
    
    # The fields to be used in displaying the User model
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_online', 'last_login', 'user_actions')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')
    
    # Fieldsets for the edit form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'profile_picture', 'date_of_birth')
        }),
        (_('Contact info'), {
            'fields': ('phone_number', 'address', 'city', 'country', 'postal_code')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse', 'wide'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse', 'wide'),
        }),
    )
    
    # Fieldsets for the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    # Custom methods for the admin interface
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(is_superuser=False)
        return qs.select_related()
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields += ('is_superuser', 'user_permissions', 'groups', 'is_staff')
        if obj and not request.user.is_superuser and obj.is_superuser:
            readonly_fields += ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
        return readonly_fields
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            form.base_fields['is_superuser'].disabled = True
            form.base_fields['user_permissions'].disabled = True
            form.base_fields['groups'].disabled = True
        return form
    
    def is_online(self, obj):
        return obj.is_online()
    is_online.boolean = True
    is_online.short_description = _('Online')
    
    def user_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>',
            reverse('admin:accounts_user_change', args=[obj.pk])
        )
    user_actions.short_description = _('Actions')
    user_actions.allow_tags = True
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/password/',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ]
        return custom_urls + urls


class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'action', 'timestamp', 'ip_address', 'user_agent_short')
    list_filter = ('timestamp', 'action')
    search_fields = ('user__email', 'action', 'ip_address', 'user_agent')
    readonly_fields = ('user', 'action', 'ip_address', 'user_agent', 'timestamp', 'user_agent_parsed')
    date_hierarchy = 'timestamp'
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('user', 'action', 'timestamp')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent_parsed'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('User')
    user_email.admin_order_field = 'user__email'
    
    def user_agent_short(self, obj):
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return ""
    user_agent_short.short_description = _('User Agent')
    
    def user_agent_parsed(self, obj):
        if not obj.user_agent:
            return ""
        return format_html('<pre>{}</pre>', obj.user_agent)
    user_agent_parsed.short_description = _('User Agent Details')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Register the custom user model
admin.site.register(User, UserAdmin)
admin.site.register(UserActivity, UserActivityAdmin)

from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _


# Unregister the default Group admin
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'permissions':
            qs = kwargs.get('queryset', db_field.remote_field.model.objects)
            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs['queryset'] = qs.select_related('content_type')
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)


# Custom admin site settings
admin.site.site_header = 'MOPDIC Administration'
admin.site.site_title = 'MOPDIC Admin'
admin.site.index_title = 'Welcome to MOPDIC Administration'

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from accounts.models import User

class Command(BaseCommand):
    help = 'Creates default groups and permissions for the admin dashboard'

    def handle(self, *args, **options):
        # Create default groups
        admin_group, created = Group.objects.get_or_create(name='Administrators')
        editor_group, created = Group.objects.get_or_create(name='Editors')
        viewer_group, created = Group.objects.get_or_create(name='Viewers')
        
        self.stdout.write(self.style.SUCCESS('Created default groups: Administrators, Editors, Viewers'))
        
        # Get all models from all installed apps
        for model in apps.get_models():
            # Skip models we don't want to assign permissions for
            if model._meta.app_label not in ['auth', 'admin', 'sessions', 'contenttypes', 'sites']:
                content_type = ContentType.objects.get_for_model(model)
                permissions = Permission.objects.filter(content_type=content_type)
                
                # Add all permissions to admin group
                admin_group.permissions.add(*permissions)
                
                # Add view and change permissions to editor group
                editor_perms = permissions.filter(
                    codename__in=['add_%s' % model._meta.model_name,
                                 'change_%s' % model._meta.model_name,
                                 'view_%s' % model._meta.model_name]
                )
                editor_group.permissions.add(*editor_perms)
                
                # Add only view permission to viewer group
                view_perm = permissions.filter(codename='view_%s' % model._meta.model_name).first()
                if view_perm:
                    viewer_group.permissions.add(view_perm)
        
        # Add additional permissions that aren't tied to models
        additional_perms = [
            'admin_logentry',
            'session',
            'permission',
            'group',
            'contenttype',
            'logentry',
        ]
        
        for perm in additional_perms:
            try:
                content_type = ContentType.objects.get(app_label='auth', model=perm)
                perms = Permission.objects.filter(content_type=content_type)
                admin_group.permissions.add(*perms)
                
                if perm in ['group', 'permission']:
                    editor_group.permissions.add(*perms)
            except ContentType.DoesNotExist:
                pass
        
        # Make sure the first superuser is in the Administrators group
        try:
            admin = User.objects.filter(is_superuser=True).first()
            if admin:
                admin.groups.add(admin_group)
                self.stdout.write(self.style.SUCCESS(f'Added superuser {admin.email} to Administrators group'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error adding superuser to admin group: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully set up default permissions'))

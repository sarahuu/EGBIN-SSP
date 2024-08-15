from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inconvenience_allowance.models import InconvenienceRequest  # Import your model

class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **kwargs):
        # Create Groups
        dept_rep_group, _ = Group.objects.get_or_create(name='Department Representatives')
        dept_member_group, _ = Group.objects.get_or_create(name='Employees')
        line_manager_group, _ = Group.objects.get_or_create(name='Line Managers')
        hr_group, _ = Group.objects.get_or_create(name='HR')

        # Define permissions
        content_type = ContentType.objects.get_for_model(InconvenienceRequest)

        dept_rep_permissions = [
            Permission.objects.get_or_create(codename='can_create_inconvenience_request',
                                             name='Can create inconvenience request',
                                             content_type=content_type)[0],
            Permission.objects.get_or_create(codename='can_edit_inconvenience_request',
                                             name='Can edit own inconvenience request',
                                             content_type=content_type)[0],
            Permission.objects.get_or_create(codename='can_delete_inconvenience_request',
                                             name='Can delete own inconvenience request',
                                             content_type=content_type)[0],
            Permission.objects.get_or_create(codename='can_certify_attendance',
                                             name='Can certify attendance',
                                             content_type=content_type)[0],
        ]

        # Assign permissions to groups
        dept_rep_group.permissions.set(dept_rep_permissions)
        self.stdout.write(self.style.SUCCESS('Groups and permissions created successfully!'))

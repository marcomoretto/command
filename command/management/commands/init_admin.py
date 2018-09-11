from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Creating admin account')
        admin = User()
        admin.username = 'admin'
        admin.set_password('admin')
        admin.is_admin = True
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()

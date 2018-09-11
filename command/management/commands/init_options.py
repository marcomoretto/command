import os

from django.core.management.base import BaseCommand

from command.lib.db.admin.admin_options import AdminOptions


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Creating default options')
        path = '/app/data/temp/download'
        os.makedirs(path, exist_ok=True)
        option = AdminOptions(option_name='download_directory', option_value=path)
        option.save()
        path = '/app/data/temp/raw_data'
        os.makedirs(path, exist_ok=True)
        option = AdminOptions(option_name='raw_data_directory', option_value=path)
        option.save()

import os

from django.conf import settings
from django.db import models

from command.lib.db.admin.compendium_type import CompendiumType


class CompendiumDatabase(models.Model):
    compendium_name = models.TextField()
    compendium_nick_name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)
    html_description = models.TextField(blank=True, null=True)
    compendium_type = models.ForeignKey(CompendiumType, on_delete=models.CASCADE, default=1, null=True)
    db_engine = models.TextField()
    db_user = models.TextField(blank=True, null=True)
    db_password = models.TextField(blank=True, null=True)
    db_port = models.TextField(blank=True, null=True)
    db_host = models.TextField(blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'compendium_name', 'compendium_nick_name', 'db_host',
                  'description', 'html_description',
                  'db_engine', 'db_user', 'db_password', 'db_port']
        compendium = {k: self.__dict__[k] for k in fields}
        compendium['compendium_type'] = self.compendium_type.to_dict()
        return compendium

    def get_setting_entry(self):
        if self.db_engine == 'SQLite':
            key = self.compendium_nick_name
            value = {
                'NAME': os.path.join(settings.BASE_DIR, self.compendium_nick_name),
                'ENGINE': 'django.db.backends.sqlite3'
            }
        else:
            key = self.compendium_nick_name
            value = {
                'NAME': self.compendium_nick_name,
                'ENGINE': self.db_engine,
                'USER': self.db_user,
                'PASSWORD': self.db_password,
                'PORT': self.db_port,
                'HOST': self.db_host
            }
        return (key, value)

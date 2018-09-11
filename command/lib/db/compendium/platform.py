from django.db import models

from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.platform_type import PlatformType
from command.lib.db.compendium.status import Status


class Platform(models.Model):
    platform_access_id = models.TextField(unique=True)
    platform_name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=False, default=1)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, blank=True, null=True)
    platform_type = models.ForeignKey(PlatformType, blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'platform_access_id', 'platform_name', 'description']
        plt_dict = {k: self.__dict__[k] for k in fields}
        plt_dict['data_source'] = self.data_source.to_dict()
        plt_dict['platform_type'] = self.platform_type.to_dict() if self.platform_type else None

        return plt_dict

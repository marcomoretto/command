from django.db import models

from command.lib.db.admin.compendium_type import CompendiumType


class PlatformTypeAdmin(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()
    bio_feature_reporter_name = models.TextField()
    compendium_type = models.ForeignKey(CompendiumType, on_delete=models.CASCADE, default=1, null=True)

    def to_dict(self):
        fields = ['id', 'name', 'description']
        plt_type = {k: self.__dict__[k] for k in fields}
        plt_type['compendium_type'] = self.compendium_type.to_dict()
        return plt_type


from django.db import models

from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.platform_type import PlatformType


class BioFeatureReporter(models.Model):
    name = models.TextField()
    description = models.TextField()
    bio_feature = models.ForeignKey(BioFeature, on_delete=models.CASCADE, default=1, null=True)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, null=False, default=1)

    class Meta:
        unique_together = ("name", "platform")

    def to_dict(self):
        fields = ['id', 'name', 'description']
        rep = {k: self.__dict__[k] for k in fields}
        rep['platform_id'] = self.platform_id
        return rep


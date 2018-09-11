
from django.db import models

from command.lib.db.compendium.platform_type import PlatformType


class BioFeatureReporterFields(models.Model):
    FEATURE_TYPE = (
        ('string', 'STRING'),
        ('float', 'FLOAT')
    )
    name = models.TextField(unique=True)
    description = models.TextField()
    platform_type = models.ForeignKey(PlatformType, on_delete=models.CASCADE, default=1, null=True)
    feature_type = models.CharField(max_length=6, choices=FEATURE_TYPE)

    def to_dict(self):
        fields = ['id', 'name', 'description', 'feature_type']
        return {k: self.__dict__[k] for k in fields}

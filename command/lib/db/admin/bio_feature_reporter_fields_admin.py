
from django.db import models

from command.lib.db.admin.platform_type_admin import PlatformTypeAdmin


class BioFeatureReporterFieldsAdmin(models.Model):
    FEATURE_TYPE = (
        ('string', 'STRING'),
        ('float', 'FLOAT')
    )
    name = models.TextField(unique=True)
    description = models.TextField()
    feature_type = models.CharField(max_length=6, choices=FEATURE_TYPE)
    platform_type = models.ForeignKey(PlatformTypeAdmin, on_delete=models.CASCADE, default=1, null=True)

    def to_dict(self):
        fields = ['id', 'name', 'description']
        return {k: self.__dict__[k] for k in fields}
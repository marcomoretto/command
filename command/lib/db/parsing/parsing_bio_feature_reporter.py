
from django.db import models

from command.lib.db.parsing.parsing_platform import ParsingPlatform


class ParsingBioFeatureReporter(models.Model):
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    platform = models.ForeignKey(ParsingPlatform, on_delete=models.CASCADE, null=False, default=1)

    class Meta:
        unique_together = ("name", "platform")

    def to_dict(self):
        fields = ['id', 'name', 'description']
        return {k: self.__dict__[k] for k in fields}


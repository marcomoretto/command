from django.db import models

from command.lib.db.compendium.normalization_type import NormalizationType


class Normalization(models.Model):
    name = models.TextField(unique=True, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    normalization_type = models.ForeignKey(NormalizationType, on_delete=models.CASCADE, null=False, default=1)
    version = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)

    def to_dict(self):
        fields = ['id', 'name', 'version', 'is_public']
        normalization_dict = {k: self.__dict__[k] for k in fields}
        normalization_dict['date'] = self.date.strftime('%Y-%m-%d %H:%M')
        normalization_dict['normalization_type'] = self.normalization_type.to_dict()
        return normalization_dict

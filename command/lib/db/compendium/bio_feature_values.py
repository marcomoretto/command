from django.db import models

from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_fields import BioFeatureFields


class BioFeatureValues(models.Model):
    bio_feature = models.ForeignKey(BioFeature, on_delete=models.CASCADE, null=False, default=1)
    bio_feature_field = models.ForeignKey(BioFeatureFields, on_delete=models.CASCADE, null=False, default=1)
    value = models.TextField()

    def to_dict(self):
        fields = ['id', 'value']
        bfv = {k: self.__dict__[k] for k in fields}
        bfv['bio_feature'] = self.bio_feature.to_dict()
        bfv['bio_feature_field'] = self.bio_feature_field.to_dict()
        return bfv


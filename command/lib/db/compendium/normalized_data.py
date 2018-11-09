from django.db import models

from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.normalization_design_group import NormalizationDesignGroup
from command.lib.db.compendium.value_type import ValueType


class NormalizedData(models.Model):
    bio_feature = models.ForeignKey(BioFeature, on_delete=models.CASCADE, default=1, null=False, blank=False)
    normalization_design_group = models.ForeignKey(NormalizationDesignGroup, on_delete=models.CASCADE, default=1, null=False, blank=False)
    value_type = models.ForeignKey(ValueType, on_delete=models.CASCADE, default=1, null=False, blank=False)
    value = models.FloatField(null=False, blank=False)
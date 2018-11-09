from django.db import models

from command.lib.db.compendium.normalization_design_group import NormalizationDesignGroup
from command.lib.db.compendium.sample import Sample


class NormalizationDesignSample(models.Model):
    normalization_design = models.ForeignKey(NormalizationDesignGroup, on_delete=models.CASCADE, null=False, default=1)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, null=False, default=1)

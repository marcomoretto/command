from django.contrib.postgres.fields import JSONField
from django.db import models

from command.lib.db.compendium.normalization_experiment import NormalizationExperiment


class NormalizationDesign(models.Model):
    normalization_experiment = models.ForeignKey(NormalizationExperiment, on_delete=models.CASCADE, null=False, default=1)
    design = JSONField(blank=True, null=True)

from django.contrib.postgres.fields import JSONField
from django.db import models

from command.lib.db.compendium.normalization_experiment import NormalizationExperiment


class NormalizationDesignGroup(models.Model):
    name = models.TextField(blank=False, null=False)
    normalization_experiment = models.ForeignKey(NormalizationExperiment, on_delete=models.CASCADE, null=False, default=1)
    design = JSONField(blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'name', 'design']
        norm_exp_dict = {k: self.__dict__[k] for k in fields}
        norm_exp_dict['normalization_experiment'] = self.normalization_experiment.to_dict()

        return norm_exp_dict

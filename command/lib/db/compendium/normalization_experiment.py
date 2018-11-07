from django.contrib.postgres.fields import JSONField
from django.db import models

from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.normalization import Normalization
from command.lib.db.compendium.status import Status


class NormalizationExperiment(models.Model):
    normalization = models.ForeignKey(Normalization, on_delete=models.CASCADE, default=1, null=False)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, default=1, null=False)
    use_experiment = models.BooleanField(default=True)
    normalization_parameters = JSONField(blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'use_experiment', 'normalization_parameters']
        exp_dict = {k: self.__dict__[k] for k in fields}
        exp_dict['experiment'] = self.experiment.to_dict()
        exp_dict['normalization'] = self.normalization.to_dict()

        return exp_dict

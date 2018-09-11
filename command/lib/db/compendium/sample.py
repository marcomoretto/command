from django.db import models

from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.platform import Platform


class Sample(models.Model):
    sample_name = models.TextField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, null=False, default=1)
    platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, blank=True, null=True, related_name='platform')
    reporter_platform = models.ForeignKey(Platform, on_delete=models.SET_NULL, blank=True, null=True, related_name='reporter_platform')

    def to_dict(self):
        fields = ['id', 'sample_name', 'description']
        sample_dict = {k: self.__dict__[k] for k in fields}
        sample_dict['experiment'] = self.experiment.to_dict()
        sample_dict['platform'] = self.platform.to_dict()
        sample_dict['reporter_platform'] = self.reporter_platform.to_dict()

        return sample_dict

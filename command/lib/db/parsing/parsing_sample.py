from django.db import models

from command.lib.db.parsing.parsing_experiment import ParsingExperiment
from command.lib.db.parsing.parsing_platform import ParsingPlatform


class ParsingSample(models.Model):
    sample_name = models.TextField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    experiment = models.ForeignKey(ParsingExperiment, on_delete=models.CASCADE, null=False, default=1)
    platform = models.ForeignKey(ParsingPlatform, on_delete=models.CASCADE, null=False, default=1)
    reporter_platform = models.PositiveIntegerField(blank=True, null=True)
    reporter_platform_imported = models.BooleanField(default=False)
    sample_fk = models.PositiveIntegerField(blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'sample_name', 'description']
        sample_dict = {k: self.__dict__[k] for k in fields}
        sample_dict['experiment'] = self.experiment.to_dict()
        sample_dict['platform'] = self.platform.to_dict()

        return sample_dict
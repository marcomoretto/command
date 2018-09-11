from django.db import models

from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.status import Status


class Experiment(models.Model):
    organism = models.TextField(blank=True, null=True)
    experiment_access_id = models.TextField(unique=True)
    experiment_name = models.TextField(blank=True, null=True)
    scientific_paper_ref = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=False, default=1)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=False, default=1)

    def to_dict(self):
        fields = ['id', 'organism', 'experiment_access_id', 'experiment_name',
                  'scientific_paper_ref', 'description']
        exp_dict = {k: self.__dict__[k] for k in fields}
        exp_dict['status'] = self.status.to_dict()
        exp_dict['data_source'] = self.data_source.to_dict()

        return exp_dict

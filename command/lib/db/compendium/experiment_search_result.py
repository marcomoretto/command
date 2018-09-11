from django.db import models

from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.status import Status


class ExperimentSearchResult(models.Model):
    ori_result_id = models.TextField(blank=True, null=True)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=False, default=1)
    organism = models.TextField(blank=True, null=True)
    experiment_access_id = models.TextField(blank=True, null=True)
    experiment_alternative_access_id = models.TextField(blank=True, null=True)
    n_samples = models.IntegerField(blank=True, null=True)
    experiment_name = models.TextField(blank=True, null=True)
    platform = models.TextField(blank=True, null=True)
    scientific_paper_ref = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=False, default=1)

    def to_dict(self):
        fields = ['id', 'ori_result_id', 'organism', 'experiment_access_id',
                  'experiment_alternative_access_id', 'n_samples', 'experiment_name',
                  'platform', 'scientific_paper_ref', 'type', 'description']
        exp_dict = {k: self.__dict__[k] for k in fields}
        exp_dict['data_source'] = self.data_source.to_dict()
        exp_dict['status'] = self.status.to_dict()
        exp_dict['date'] = self.date.strftime('%Y-%m-%d')

        return exp_dict

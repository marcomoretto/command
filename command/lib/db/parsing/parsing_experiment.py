from django.db import models


class ParsingExperiment(models.Model):
    organism = models.TextField(blank=True, null=True)
    experiment_access_id = models.TextField(unique=True)
    experiment_name = models.TextField(blank=True, null=True)
    scientific_paper_ref = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    experiment_fk = models.PositiveIntegerField(blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'organism', 'experiment_access_id', 'experiment_name',
                  'scientific_paper_ref', 'description']
        exp_dict = {k: self.__dict__[k] for k in fields}

        return exp_dict
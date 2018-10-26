from django.contrib.postgres.fields import JSONField
from django.db import models


class Ontology(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    original_filename = models.TextField(blank=True, null=True)
    is_biofeature = models.BooleanField(default=False)
    is_sample = models.BooleanField(default=False)
    json = JSONField(blank=True, null=True)

    def to_dict(self, columns=False):
        fields = ['id', 'name', 'description', 'is_biofeature', 'is_sample']
        ontology_dict = {}
        for k in fields:
            ontology_dict[k] = self.__dict__[k]
        if columns:
            ontology_dict['columns'] = self.get_columns()

        return ontology_dict

    def get_columns(self):
        return self.json['columns'] if self.json and 'columns' in self.json else []

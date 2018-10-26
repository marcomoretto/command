from django.contrib.postgres.fields import JSONField
from django.db import models

from command.lib.db.compendium.ontology import Ontology


class OntologyNode(models.Model):
    original_id = models.TextField(db_index=True)
    ontology = models.ForeignKey(Ontology, on_delete=models.CASCADE, null=False, default=1)
    json = JSONField(blank=True, null=True)

    class Meta:
        unique_together = ('original_id', 'ontology',)

    def to_dict(self):
        fields = ['id', 'original_id']
        ontology_node_dict = {k: self.__dict__[k] for k in fields}

        return ontology_node_dict
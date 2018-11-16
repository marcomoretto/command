from django.contrib.postgres.fields import JSONField
from django.db import models

from command.lib.db.compendium.ontology import Ontology
from command.lib.db.compendium.ontology_node import OntologyNode


class OntologyEdge(models.Model):
    source = models.ForeignKey(OntologyNode, on_delete=models.CASCADE, null=False, default=1, related_name='ontology_node_source')
    target = models.ForeignKey(OntologyNode, on_delete=models.CASCADE, null=False, default=1, related_name='ontology_node_target')
    is_directed = models.BooleanField(default=False)
    edge_type = models.TextField(blank=True, null=True, db_index=True)
    ontology = models.ForeignKey(Ontology, on_delete=models.CASCADE, null=False, default=1)
    json = JSONField(blank=True, null=True)

    class Meta:
        unique_together = ('source', 'target', 'edge_type', 'ontology')

    def to_dict(self):
        fields = ['id', 'name']
        ontology_node_dict = {k: self.__dict__[k] for k in fields}

        return ontology_node_dict

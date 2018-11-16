from django.db import models

from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.ontology_node import OntologyNode


class BioFeatureAnnotation(models.Model):
    bio_feature = models.ForeignKey(BioFeature, on_delete=models.CASCADE, default=1, null=False, blank=False)
    ontology_node = models.ForeignKey(OntologyNode, on_delete=models.CASCADE, default=1, null=False, blank=False)

    class Meta:
        unique_together = ('bio_feature', 'ontology_node',)

    def to_dict(self):
        fields = ['id', 'bio_feature_id', 'ontology_node_id']
        return {k: self.__dict__[k] for k in fields}

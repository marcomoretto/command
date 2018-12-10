from django.db import models

from command.lib.db.compendium.annotation_value import AnnotationValue
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.ontology_node import OntologyNode


class BioFeatureAnnotation(models.Model):
    bio_feature = models.ForeignKey(BioFeature, on_delete=models.CASCADE, default=1, null=False, blank=False)
    annotation_value = models.ForeignKey(AnnotationValue, on_delete=models.CASCADE, null=False, default=1)

    class Meta:
        unique_together = ('bio_feature', 'annotation_value')

    def to_dict(self):
        fields = ['id', 'bio_feature_id', 'annotation_value_id']
        return {k: self.__dict__[k] for k in fields}

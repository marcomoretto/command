from django.db import models

from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.ontology_node import OntologyNode
from command.lib.db.compendium.platform import Platform


class AnnotationValue(models.Model):
    VALUE_TYPE = (
        ('number', 'NUMBER'),
        ('string', 'STRING'),
        ('boolean', 'BOOLEAN')
    )
    ontology_node = models.ForeignKey(OntologyNode, on_delete=models.CASCADE, null=False, default=1)
    value = models.TextField(blank=False, null=False, default='True')
    value_type = models.CharField(max_length=7, choices=VALUE_TYPE, blank=False, null=False, default='boolean')
    value_annotation = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, default=None)
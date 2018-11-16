from django.db import models

from command.lib.db.compendium.annotation_value import AnnotationValue
from command.lib.db.compendium.sample import Sample


class SampleAnnotation(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, null=False, default=1)
    annotation_value = models.ForeignKey(AnnotationValue, on_delete=models.CASCADE, null=False, default=1)


from django.db import models

from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_fields import BioFeatureFields
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.bio_feature_reporter_fields import BioFeatureReporterFields


class BioFeatureReporterValues(models.Model):
    bio_feature_reporter = models.ForeignKey(BioFeatureReporter, on_delete=models.CASCADE, null=False, default=1)
    bio_feature_reporter_field = models.ForeignKey(BioFeatureReporterFields, on_delete=models.CASCADE, null=False, default=1)
    value = models.TextField()

    class Meta:
        unique_together = ("bio_feature_reporter", "bio_feature_reporter_field")


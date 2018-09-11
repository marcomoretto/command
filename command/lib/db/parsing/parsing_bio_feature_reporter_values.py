from django.db import models

from command.lib.db.parsing.parsing_bio_feature_reporter import ParsingBioFeatureReporter


class ParsingBioFeatureReporterValues(models.Model):
    bio_feature_reporter = models.ForeignKey(ParsingBioFeatureReporter, on_delete=models.CASCADE, null=False, default=1)
    bio_feature_reporter_field = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)


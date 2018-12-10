from django.db import models

from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.sample import Sample
from command.lib.db.compendium.value_type import ValueType


class RawData(models.Model):
    sample = models.ForeignKey(Sample, db_index=True, on_delete=models.CASCADE, null=False, default=1)
    bio_feature_reporter = models.ForeignKey(BioFeatureReporter, db_index=True, on_delete=models.CASCADE, null=False, default=1)
    value = models.FloatField(blank=True, null=True)
    value_type = models.ForeignKey(ValueType, on_delete=models.CASCADE, default=1, null=True, blank=True)

    def to_dict(self, reduced=False):
        fields = ['id', 'value']
        rd_dict = {k: self.__dict__[k] for k in fields}
        if reduced:
            rd_dict['bio_feature_reporter_name'] = self.bio_feature_reporter.name
        else:
            rd_dict['sample'] = self.sample.to_dict()
            rd_dict['bio_feature_reporter'] = self.bio_feature_reporter.to_dict()

        return rd_dict
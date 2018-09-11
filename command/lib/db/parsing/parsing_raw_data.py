from django.db import models

from command.lib.db.parsing.parsing_sample import ParsingSample


class ParsingRawData(models.Model):
    sample = models.ForeignKey(ParsingSample, on_delete=models.CASCADE, null=False, default=1)
    bio_feature_reporter_name = models.TextField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'bio_feature_reporter_name', 'value']
        rd_dict = {k: self.__dict__[k] for k in fields}
        rd_dict['sample'] = self.sample.to_dict()

        return rd_dict
from django.db import models


class BioFeatureFields(models.Model):
    FEATURE_TYPE = (
        ('string', 'STRING'),
        ('float', 'FLOAT')
    )
    name = models.TextField()
    description = models.TextField()
    feature_type = models.CharField(max_length=6, choices=FEATURE_TYPE)

    def to_dict(self):
        fields = ['id', 'name', 'description', 'feature_type']
        return {k: self.__dict__[k] for k in fields}

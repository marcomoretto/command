from django.db import models


class PlatformType(models.Model):
    name = models.TextField()
    description = models.TextField()
    bio_feature_reporter_name = models.TextField()

    def to_dict(self):
        fields = ['id', 'name', 'description', 'bio_feature_reporter_name']
        plt_type = {k: self.__dict__[k] for k in fields}
        plt_type['bio_features_reporter_fields'] = [field.to_dict()
                                                    for field in self.biofeaturereporterfields_set.all()]
        return plt_type

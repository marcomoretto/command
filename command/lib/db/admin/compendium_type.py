from django.db import models


class CompendiumType(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()
    bio_feature_name = models.TextField()

    def to_dict(self):
        fields = ['id', 'name', 'description', 'bio_feature_name']
        return {k: self.__dict__[k] for k in fields}
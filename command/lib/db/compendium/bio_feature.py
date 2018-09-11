from django.db import models


class BioFeature(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()

    def to_dict(self):
        fields = ['id', 'name', 'description']
        return {k: self.__dict__[k] for k in fields}

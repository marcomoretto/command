from django.db import models


class NormalizationType(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()
    python_class = models.TextField()

    def to_dict(self):
        fields = ['id', 'name', 'description']
        type_dict = {k: self.__dict__[k] for k in fields}

        return type_dict

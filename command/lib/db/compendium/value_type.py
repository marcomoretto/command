from django.db import models


class ValueType(models.Model):
    name = models.TextField(blank=False, unique=True)
    description = models.TextField(blank=True, null=True)

    def to_dict(self):
        fields = ['id', 'name', 'description']
        return {k: self.__dict__[k] for k in fields}






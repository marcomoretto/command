from django.db import models


class DataSource(models.Model):
    source_name = models.TextField()
    python_class = models.TextField()
    is_local = models.BooleanField(default=False)

    def to_dict(self):
        fields = ['id', 'source_name', 'python_class', 'is_local']
        return {k: self.__dict__[k] for k in fields}






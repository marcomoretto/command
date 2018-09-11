from django.db import models


class AdminOptions(models.Model):
    option_name = models.TextField(blank=False, unique=True, default='')
    option_value = models.TextField(blank=False)

    def to_dict(self):
        fields = ['option_name', 'option_value']
        return {k: self.__dict__[k] for k in fields}





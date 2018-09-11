from django.db import models


class ParsingPlatform(models.Model):
    platform_access_id = models.TextField(unique=True)
    platform_name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    platform_type = models.TextField(blank=True, null=True)
    platform_fk = models.PositiveIntegerField(blank=True, null=True)
    reporter_platform = models.PositiveIntegerField(blank=True, null=True)
    reporter_platform_imported = models.BooleanField(default=False)

    def to_dict(self):
        fields = ['id', 'platform_access_id', 'platform_name', 'description', 'platform_type']
        plt_dict = {k: self.__dict__[k] for k in fields}
        
        return plt_dict

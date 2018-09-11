from django.db import models


class ViewTask(models.Model):
    task_id = models.TextField(blank=True, null=True)
    operation = models.TextField(blank=True, null=True)
    view = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('operation', 'view')





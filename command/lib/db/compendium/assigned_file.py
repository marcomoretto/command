from django.db import models

from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample


class AssignedFile(models.Model):
    ENTITY_TYPE = (
        ('EXP', 'EXPERIMENT'),
        ('PLT', 'PLATFORM'),
        ('SMP', 'SAMPLE')
    )
    script_name = models.TextField(blank=True, null=True)
    input_filename = models.TextField(blank=True, null=True)
    parameters = models.TextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    entity_type = models.CharField(max_length=3, choices=ENTITY_TYPE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, blank=True, null=True, default=None)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, blank=True, null=True, default=None)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, blank=True, null=True, default=None)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, blank=True, null=True, default=None)
    message_log = models.ForeignKey(MessageLog, on_delete=models.SET_NULL, blank=True, null=True, default=None)

    def to_dict(self):
        fields = ['id', 'script_name', 'input_filename', 'parameters', 'order', 'entity_type']
        af = {k: self.__dict__[k] for k in fields}
        af['message_log'] = self.message_log.to_dict() if self.message_log else None
        return af

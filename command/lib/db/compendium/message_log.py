from django.db import models

class MessageLog(models.Model):
    SOURCE = (
        ('User', 'USER'),
        ('System', 'SYSTEM')
    )
    title = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=6, choices=SOURCE)

    _command_view = 'message_log'

    def to_dict(self):
        fields = ['id', 'title', 'message', 'source']
        message_dict = {k: self.__dict__[k] for k in fields}
        message_dict['date'] = self.date.strftime('%Y-%m-%d %H:%M')

        return message_dict

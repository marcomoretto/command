import json

from channels import Group
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.message_log import MessageLog


@receiver(post_save, sender=MessageLog)
def save_log_message(sender, instance, **kwargs):
    compendium = CompendiumDatabase.objects.get(compendium_nick_name=kwargs['using'])
    Group("compendium_" + str(compendium.id)).send({
        'text': json.dumps({
            'stream': sender._command_view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })
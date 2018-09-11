import json
import os

import celery
from channels import Group, Channel
from django.contrib.auth.models import User
from django.db import connections

from command.lib.coll.biological_feature import importers
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.message_log import MessageLog
from command.lib.utils.message import Message
from command.models import init_database_connections


class RunParsingBioFeatureFileCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, file_path, bio_feature_name, file_type, channel_name, view, operation = args
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': 'bio_feature',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        log = MessageLog()
        log.title = "Importing " + bio_feature_name + " (biological features) from " + file_type + " file"
        log.message = "Status: success, File: " + os.path.basename(file_path) + ", Type: " + file_type + \
                      ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, file_path, bio_feature_name, file_type, channel_name, view, operation = args
        channel = Channel(channel_name)
        message = Message(type='error', title='Error', message=str(exc))
        message.send_to(channel)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        log = MessageLog()
        log.title = "Importing " + bio_feature_name + " (biological features) from " + file_type + " file"
        log.message = "Status: error, File: " + os.path.basename(file_path) + ", Type: " + file_type + \
                      ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                      "Exception: " + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)


@celery.task(base=RunParsingBioFeatureFileCallbackTask, bind=True)
def run_parsing_bio_feature(self, user_id, compendium_id, file_path, bio_feature_name, file_type,
             channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id

    parser_cls = None
    for cls in importers.importer_mapping[bio_feature_name]:
        if cls.FILE_TYPE_NAME == file_type:
            parser_cls = cls
            break

    parser = parser_cls(compendium.compendium_nick_name, bio_feature_name)
    parser.parse(file_path)

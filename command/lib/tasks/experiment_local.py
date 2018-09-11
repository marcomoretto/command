from __future__ import absolute_import, unicode_literals

import json
import os

import celery
from channels import Group, Channel
from django.contrib.auth.models import User
from django.db import connections

from command.lib.coll.local_data_source import LocalDataSource
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.utils.message import Message
from command.models import init_database_connections


class ExperimentLocalUploadCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, exp_id, exp_name, exp_descr, exp_structure_file, exp_data_file, \
            channel_name, view, operation = args
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': 'experiments',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, exp_id, exp_name, exp_descr, exp_structure_file, exp_data_file, \
            channel_name, view, operation = args
        channel = Channel(channel_name)
        message = Message(type='error', title='Error on experiment ' + exp_name, message=str(exc))
        message.send_to(channel)


@celery.task(base=ExperimentLocalUploadCallbackTask, bind=True)
def experiment_local_upload(self, user_id, compendium_id, exp_id, exp_name, exp_descr, exp_structure_file,
                            exp_data_file, channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    operation = operation + "_" + str(exp_id)

    base_dir = AdminOptions.objects.get(option_name='download_directory')
    base_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name, exp_id)

    exp_file = os.path.join(base_dir, exp_data_file)

    local_data_source = LocalDataSource()
    local_data_source.uncompress_experiment_file(exp_file, base_dir)
    os.rename(os.path.join(base_dir, exp_structure_file),
              os.path.join(base_dir, local_data_source.experiment_structure_filename))
    local_data_source.create_experiment_structure(compendium_id, exp_id, base_dir)



from __future__ import absolute_import, unicode_literals

import json
import os

import celery
from channels import Group
from django.contrib.auth.models import User
from django.db import connections

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.experiment import Experiment
from command.lib.utils import file_system
from command.models import init_database_connections


class UncompressFileCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, exp_id, filename, channel_name, view, operation = args
        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        pass


@celery.task(base=UncompressFileCallbackTask, bind=True)
def uncompress_file(self, user_id, compendium_id, exp_id, filename, channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    operation = operation + "_" + str(exp_id)
    exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)

    base_dir = AdminOptions.objects.get(option_name='download_directory')
    base_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name, exp.experiment_access_id)

    exp_file = os.path.join(base_dir, filename)

    file_system.uncompress_file(exp_file, base_dir)



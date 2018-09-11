from __future__ import absolute_import, unicode_literals

import importlib
import json
import os

import celery
from celery.contrib.abortable import AbortableTask
from channels import Group, Channel
from django.contrib.auth.models import User
from django.db import connections
from django.db.models import Q

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.experiment_search_result import ExperimentSearchResult
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.view_task import ViewTask
from command.lib.utils.message import Message
from command.models import init_database_connections


class ExperimentPublicSearchCallbackTask(AbortableTask, celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, term, db_id, channel_name, view, operation = args

        compendium = CompendiumDatabase.objects.get(id=compendium_id)

        log = MessageLog()
        log.title = "Search experiment " + term
        log.message = "Status: success, Term: " + term + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        ViewTask.objects.using(compendium.compendium_nick_name). \
            get(task_id=task_id, operation=operation, view=view).delete()

        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, term, db_id, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)

        log = MessageLog()
        log.title = "Search experiment " + term
        log.message = "Status: error, Term: " + term + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username + \
                      "Exception: " + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        message = Message(type='error', title='Error', message=str(exc))
        message.send_to(channel)

        ViewTask.objects.using(compendium.compendium_nick_name). \
            get(task_id=task_id, operation=operation, view=view).delete()

        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })


class ExperimentPublicDownloadCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, experiment_id, channel_name, view, operation = args
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': 'experiments',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=experiment_id)

        log = MessageLog()
        log.title = "Download experiment " + exp.experiment_access_id
        log.message = "Status: success, Experiment: " + exp.experiment_access_id + ", Task: " + task_id + "," \
                        "User: " + User.objects.get(id=user_id).username + \
                        "Notes: " + retval
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)
        if retval:
            channel = Channel(channel_name)
            message = Message(type='info', title='Download notes', message="Duplicated samples are not imported! <br><br>" + retval)
            message.send_to(channel)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, experiment_id, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        new_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_new')
        exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
        exp.status = new_status
        exp.save(using=compendium.compendium_nick_name)
        log = MessageLog()
        log.title = "Download experiment " + exp.experiment_access_id
        log.message = "Status: error, Experiment: " + exp.experiment_access_id + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username + \
                      "Exception: " + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)
        message = Message(type='error', title='Error on experiment ' + exp.experiment_access_id, message=str(exc))
        message.send_to(channel)
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': 'experiments',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })


@celery.task(base=ExperimentPublicDownloadCallbackTask, bind=True)
def experiment_public_download(self, user_id, compendium_id, experiment_id, channel_name, view, operation):
    init_database_connections()
    channel = Channel(channel_name)
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    operation = operation + "_" + str(experiment_id)
    downloading_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_downloading')
    exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
    exp.status = downloading_status
    exp.save(using=compendium.compendium_nick_name)
    try:
        ViewTask.objects.using(compendium.compendium_nick_name). \
            get(operation=operation, view=view).delete()
    except Exception as e:
        pass
    channel_task = ViewTask(task_id=task_id, operation=operation,
                            view=view)
    channel_task.save(using=compendium.compendium_nick_name)
    data_ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_data_ready')
    base_output_directory = AdminOptions.objects.get(option_name='download_directory')
    exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
    out_dir = os.path.join(base_output_directory.option_value, compendium.compendium_nick_name, exp.experiment_access_id)
    os.makedirs(out_dir, exist_ok=True)
    Group("compendium_" + str(compendium_id)).send({
        'text': json.dumps({
            'stream': view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })
    log_message = ''
    module_name, class_name = '.'.join(exp.data_source.python_class.split('.')[:-1]), \
                              exp.data_source.python_class.split('.')[-1]
    python_class = getattr(importlib.import_module(module_name), class_name)()
    python_class.download_experiment_files(exp.experiment_access_id, user.email, out_dir)
    try:
        Experiment.objects.using(compendium.compendium_nick_name).get(experiment_access_id=
                                                                      exp.experiment_access_id)
        message = Message(type='info', title='Experiment already exists', message=
                          'The experiment ' + exp.experiment_access_id + ' is already present in the database. Data have been download anyway.')
        message.send_to(channel)
    except Exception as e:
        log_message = python_class.create_experiment_structure(compendium_id, experiment_id, out_dir)
    exp.status = data_ready_status
    exp.save(using=compendium.compendium_nick_name)

    return log_message


@celery.task(base=ExperimentPublicSearchCallbackTask, bind=True)
def experiment_public_search(self, user_id, compendium_id, term, db_id, channel_name, view, operation):
    init_database_connections()
    channel = Channel(channel_name)
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    try:
        ViewTask.objects.using(compendium.compendium_nick_name). \
            get(view=view, operation=operation).delete()
    except Exception as e:
        pass
    channel_task = ViewTask(task_id=task_id, operation=operation, view=view)
    channel_task.save(using=compendium.compendium_nick_name)

    public_db_class_name = DataSource.objects.using(compendium.compendium_nick_name).get(id=db_id)
    Group("compendium_" + str(compendium_id)).send({
        'text': json.dumps({
            'stream': view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })
    module_name, class_name = '.'.join(public_db_class_name.python_class.split('.')[:-1]), public_db_class_name.python_class.split('.')[-1]
    python_class = getattr(importlib.import_module(module_name), class_name)()
    results = python_class.search(term, user.email, db_id, self.is_aborted)
    experiment_status_download = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_new')
    for result in results:
        result.status = experiment_status_download
    ExperimentSearchResult.objects.using(compendium.compendium_nick_name).filter(
        ~Q(status__name='experiment_scheduled') & ~Q(status__name='experiment_downloading')
    ).delete()
    ExperimentSearchResult.objects.using(compendium.compendium_nick_name).bulk_create(results)

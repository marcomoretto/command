import json
import os
import sys
from io import StringIO

import celery
from channels import Channel, Group
from django.contrib.auth.models import User
from django.db import connections

from command.lib import parsing_scripts
from command.lib.coll import soft_file_parser
from command.lib.coll.experiment_proxy import ExperimentProxy
from command.lib.coll.platform_proxy import PlatformProxy
from command.lib.coll.sample_proxy import SampleProxy
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.utils.message import Message
from command.models import init_database_connections
from django.conf import settings


class RunParsingScriptCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, exp_id, entity_type, entity_id, channel_name, view, operation = args

        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)
        parsed_status = Status.objects.using(compendium.compendium_nick_name).get(name='entity_script_parsed')
        entity_access_id = ''
        if entity_type == 'experiment':
            entity_access_id = exp.experiment_access_id
            for af in exp.assignedfile_set.all():
                log = MessageLog()
                log.title = exp.experiment_access_id + " " + af.script_name + " completed on file " + af.input_filename
                log.message = "Status: success, Experiment: " + exp.experiment_access_id + ", Order: " + str(
                    af.order) + ", Parameters: " + " ".join(af.parameters) + " Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
                log.source = log.SOURCE[1][0]
                log.save(using=compendium.compendium_nick_name)
                af.status = parsed_status
                af.message_log = log
                af.save(using=compendium.compendium_nick_name)
        elif entity_type == 'platform':
            platform = Platform.objects.using(compendium.compendium_nick_name).get(id=entity_id)
            entity_access_id = platform.platform_access_id
            for af in platform.assignedfile_set.all():
                log = MessageLog()
                log.title = exp.experiment_access_id + " " + af.script_name + " completed on file " + af.input_filename
                log.message = "Status: success, Platform: " + platform.platform_access_id + ", Order: " + str(
                    af.order) + ", Parameters: " + " ".join(
                    af.parameters) + " Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
                log.source = log.SOURCE[1][0]
                log.save(using=compendium.compendium_nick_name)
                af.status = parsed_status
                af.message_log = log
                af.save(using=compendium.compendium_nick_name)
        elif entity_type == 'sample':
            sample = Sample.objects.using(compendium.compendium_nick_name).get(experiment=exp, id=entity_id)
            entity_access_id = sample.sample_name
            for af in sample.assignedfile_set.all():
                log = MessageLog()
                log.title = exp.experiment_access_id + " " + af.script_name + " completed on file " + af.input_filename
                log.message = "Status: success, Sample: " + sample.sample_name + ", Order: " + str(
                    af.order) + ", Parameters: " + " ".join(
                    af.parameters) + " Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
                log.source = log.SOURCE[1][0]
                log.save(using=compendium.compendium_nick_name)
                af.status = parsed_status
                af.message_log = log
                af.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': 'parse_experiment_platform',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': 'message_log',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': 'file_assignment_list',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        if retval:
            message = Message(type='parsing_log', title='Parsing STDOUT ' + entity_type + ' ' + entity_access_id +
                                                 ', experiment: ' + exp.experiment_access_id,
                              message=retval.replace('\n', '<br>'))
            message.send_to(channel)


    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, exp_id, entity_type, entity_id, channel_name, view, operation = args
        channel = Channel(channel_name)

        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)
        error_status = Status.objects.using(compendium.compendium_nick_name).get(name='entity_script_error')
        access_id = ''
        if entity_type == 'experiment':
            for af in exp.assignedfile_set.all():
                log = MessageLog()
                log.title = exp.experiment_access_id + " " + af.script_name + " error on file " + af.input_filename
                log.message = "Status: error, Experiment: " + exp.experiment_access_id + ", Order: " + str(
                    af.order) + ", Parameters: " + " ".join(
                    af.parameters) + " Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                              ", Exception: " + str(exc) + ", Stacktrace: " + \
                              einfo.traceback
                log.source = log.SOURCE[1][0]
                log.save(using=compendium.compendium_nick_name)
                af.status = error_status
                af.message_log = log
                af.save(using=compendium.compendium_nick_name)
        elif entity_type == 'platform':
            platform = Platform.objects.using(compendium.compendium_nick_name).get(id=entity_id)
            for af in platform.assignedfile_set.all():
                log = MessageLog()
                log.title = exp.experiment_access_id + " " + af.script_name + " error on file " + af.input_filename
                log.message = "Status: error, Platform: " + platform.platform_access_id + ", Order: " + str(
                    af.order) + ", Parameters: " + " ".join(
                    af.parameters) + " Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                              ", Exception: " + str(exc) + ", Stacktrace: " + \
                              einfo.traceback
                log.source = log.SOURCE[1][0]
                log.save(using=compendium.compendium_nick_name)
                af.status = error_status
                af.message_log = log
                af.save(using=compendium.compendium_nick_name)
        elif entity_type == 'sample':
            sample = Sample.objects.using(compendium.compendium_nick_name).get(experiment=exp, id=entity_id)
            access_id = sample.sample_name
            for af in sample.assignedfile_set.all():
                log = MessageLog()
                log.title = exp.experiment_access_id + " " + af.script_name + " error on file " + af.input_filename
                log.message = "Status: error, Sample: " + sample.sample_name + ", Order: " + str(
                    af.order) + ", Parameters: " + " ".join(
                    af.parameters) + " Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                              ", Exception: " + str(exc) + ", Stacktrace: " + \
                              einfo.traceback
                log.source = log.SOURCE[1][0]
                log.save(using=compendium.compendium_nick_name)
                af.status = error_status
                af.message_log = log
                af.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': 'message_log',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': 'file_assignment',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        message = Message(type='error', title='Error parsing ' + entity_type + ' ' + access_id, message=str(exc))
        message.send_to(channel)


@celery.task(base=RunParsingScriptCallbackTask, bind=True)
def run_parsing_script(self, user_id, compendium_id, exp_id, entity_type, entity_name, channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    operation = operation + "_" + str(exp_id)
    exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)
    sample = None
    platform = None
    entity_object_name = None
    running_status = Status.objects.using(compendium.compendium_nick_name).get(name='entity_script_running')
    assigned_files = []
    base_path = os.path.dirname(parsing_scripts.__file__)
    if entity_type == 'experiment':
        entity_object_name = exp.experiment_access_id
        for af in exp.assignedfile_set.all():
            af.status = running_status
            af.save(using=compendium.compendium_nick_name)
            af_dict = af.to_dict()
            af_dict['script_name'] = os.path.join(base_path, entity_type, af_dict['script_name'])
            af_dict['order'] = 0 if not af_dict['order'] else int(af_dict['order'])
            assigned_files.append(af_dict)
    elif entity_type == 'platform':
        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=entity_name)
        entity_object_name = platform.platform_access_id
        for af in platform.assignedfile_set.all():
            af.status = running_status
            af.save(using=compendium.compendium_nick_name)
            af_dict = af.to_dict()
            af_dict['script_name'] = os.path.join(base_path, entity_type, af_dict['script_name'])
            af_dict['order'] = 0 if not af_dict['order'] else int(af_dict['order'])
            assigned_files.append(af_dict)
    elif entity_type == 'sample':
        sample = Sample.objects.using(compendium.compendium_nick_name).get(experiment=exp, id=entity_name)
        entity_object_name = sample.sample_name
        for af in sample.assignedfile_set.all():
            af.status = running_status
            af.save(using=compendium.compendium_nick_name)
            af_dict = af.to_dict()
            af_dict['script_name'] = os.path.join(base_path, entity_type, af_dict['script_name'])
            af_dict['order'] = 0 if not af_dict['order'] else int(af_dict['order'])
            assigned_files.append(af_dict)
    assigned_files.sort(key=lambda x: int(x['order']))

    Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
        'text': json.dumps({
            'stream': entity_type + "_" + view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })

    base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
    out_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                           exp.experiment_access_id)
    key = os.path.join(out_dir, exp.experiment_access_id + '.sqlite')

    buffer = StringIO()
    sys.stdout = buffer
    context = {}
    soft_parser_dir = os.path.dirname(soft_file_parser.__file__)
    input_file_dir = AdminOptions.objects.get(option_name='download_directory').option_value
    input_file_dir = os.path.join(input_file_dir, compendium.compendium_nick_name, exp.experiment_access_id)
    experiment_proxy = ExperimentProxy(exp, key) if entity_type == 'experiment' else None
    platform_proxy = PlatformProxy(platform, key) if entity_type == 'platform' else None
    sample_proxy = SampleProxy(sample, key) if entity_type == 'sample' else None
    for assigned_file in assigned_files:
        script = assigned_file['script_name']
        if os.path.isfile(script) and script.endswith('.py'):
            input_file_value = os.path.join(input_file_dir, assigned_file['input_filename'])
            context = {
                'PARAMETERS': [p.strip() for p in assigned_file['parameters'].split(',')],
                'INPUT_FILE': input_file_value,
                'ENTITY_NAME': entity_object_name,
                'EXPERIMENT_OBJECT': experiment_proxy,
                'PLATFORM_OBJECT': platform_proxy,
                'SAMPLE_OBJECT': sample_proxy,
                'COMPENDIUM': compendium.compendium_nick_name
            }
            script_dir = os.path.dirname(script)
            util_dir = os.path.join(os.path.dirname(script_dir), 'utils')
            sys.path.append(script_dir)
            sys.path.append(util_dir)
            sys.path.append(soft_parser_dir)
            exec(open(script).read(), context)

    sys.stdout = sys.__stdout__

    if 'EXPERIMENT_OBJECT' in context and isinstance(context['EXPERIMENT_OBJECT'], ExperimentProxy):
        context['EXPERIMENT_OBJECT'].save_experiment_object()
    if 'PLATFORM_OBJECT' in context and isinstance(context['PLATFORM_OBJECT'], PlatformProxy):
        context['PLATFORM_OBJECT'].save_platform_object()
    if 'SAMPLE_OBJECT' in context and isinstance(context['SAMPLE_OBJECT'], SampleProxy):
        context['SAMPLE_OBJECT'].save_sample_object()

    return buffer.getvalue()

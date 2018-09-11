import json
import os
import sys
from io import StringIO

import celery
from channels import Channel, Group
from django.contrib.auth.models import User
from django.db import connections, transaction

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.assigned_file import AssignedFile
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.sample import Sample
from command.lib.utils.message import Message
from command.models import init_database_connections
from django.conf import settings
from command.lib import parsing_scripts

class RunFileAssignmentScriptCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, exp_id, script, parameters, input_files,\
            experiment_entity, platform_entity, sample_entity, channel_name, view, operation = args
        channel = Channel(channel_name)
        message = Message(type='info', title='Assigned script run succesfully.', message=retval[0])
        message.send_to(channel)
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
                'stream': 'experiment_' + view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': 'platform_' + view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group("compendium_" + str(compendium_id) + "_" + str(exp_id)).send({
            'text': json.dumps({
                'stream': 'sample_' + view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        if retval[1]:
            message = Message(type='parsing_log', title='Assignment script',
                              message=retval[1].replace('\n', '<br>'))
            message.send_to(channel)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, exp_id, script, parameters, input_files,\
            experiment_entity, platform_entity, sample_entity, channel_name, view, operation = args
        channel = Channel(channel_name)
        message = Message(type='error', title='Error running ' + os.path.basename(script), message=str(exc))
        message.send_to(channel)


@celery.task(base=RunFileAssignmentScriptCallbackTask, bind=True)
def run_file_assignment_script(self, user_id, compendium_id, exp_id, script_filename, parameters, input_files,
                               experiment_entity, platform_entity, sample_entity, channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    operation = operation + "_" + str(exp_id)
    exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)

    base_path = os.path.join(os.path.dirname(parsing_scripts.__file__), 'file_assignment')
    script = os.path.join(base_path, script_filename)

    buffer = StringIO()
    message = ""
    if os.path.isfile(script) and script.endswith('.py'):
        context = {
            'PARAMETERS': parameters.split(','),
            'INPUT_FILES': input_files
        }
        sys.stdout = buffer
        script_dir = os.path.dirname(script)
        util_dir = os.path.join(os.path.dirname(script_dir), 'utils')
        sys.path.append(script_dir)
        sys.path.append(util_dir)
        exec(open(script).read(), context)
        assign_function = context['assign']
        ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='entity_script_ready')
        message = "Assigned "
        with transaction.atomic(using=compendium.compendium_nick_name):
            files = assign_function(context['INPUT_FILES'], exp.to_dict(), 'experiment', context['PARAMETERS'])
            file_counter = 0
            for file in files:
                if not experiment_entity[0]:
                    continue
                file_counter += 1
                assigned_file = AssignedFile()
                assigned_file.script_name = experiment_entity[0]
                assigned_file.order = experiment_entity[1]
                assigned_file.parameters = experiment_entity[2]
                assigned_file.input_filename = os.path.basename(file)
                assigned_file.entity_type = 'EXP'
                assigned_file.experiment = exp
                assigned_file.status = ready_status
                assigned_file.save(using=compendium.compendium_nick_name)
            message += str(file_counter) + " files to EXPERIMENT, "
            platforms = set()
            file_counter = 0
            for sample in Sample.objects.using(compendium.compendium_nick_name).filter(experiment=exp):
                platforms.add(sample.platform)
                files = assign_function(context['INPUT_FILES'], sample.to_dict(), 'sample', context['PARAMETERS'])
                for file in files:
                    if not sample_entity[0]:
                        continue
                    file_counter += 1
                    assigned_file = AssignedFile()
                    assigned_file.script_name = sample_entity[0]
                    assigned_file.order = sample_entity[1]
                    assigned_file.parameters = sample_entity[2]
                    assigned_file.input_filename = os.path.basename(file)
                    assigned_file.entity_type = 'SMP'
                    assigned_file.sample = sample
                    assigned_file.status = ready_status
                    assigned_file.save(using=compendium.compendium_nick_name)
            message += str(file_counter) + " files to SAMPLES, "
            file_counter = 0
            for platform in platforms:
                files = assign_function(context['INPUT_FILES'], platform.to_dict(), 'platform', context['PARAMETERS'])
                for file in files:
                    if not platform_entity[0]:
                        continue
                    file_counter += 1
                    assigned_file = AssignedFile()
                    assigned_file.script_name = platform_entity[0]
                    assigned_file.order = platform_entity[1]
                    assigned_file.parameters = platform_entity[2]
                    assigned_file.input_filename = os.path.basename(file)
                    assigned_file.entity_type = 'PLT'
                    assigned_file.platform = platform
                    assigned_file.status = ready_status
                    assigned_file.save(using=compendium.compendium_nick_name)
            message += str(file_counter) + " files to PLATFORMS"
    sys.stdout = sys.__stdout__

    return message, buffer.getvalue()

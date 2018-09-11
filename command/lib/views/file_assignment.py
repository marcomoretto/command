import glob
import json
import os
import time

from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.assigned_file import AssignedFile
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.db.parsing.parsing_platform import ParsingPlatform
from command.lib.tasks import run_file_assignment_script, run_parsing_script
from command.lib.tasks import uncompress_file
from command.lib.utils.decorators import forward_exception_to_http, forward_exception_to_channel, check_permission
#from command.lib.utils.group_compendium_permission import GroupCompendiumPermission
from command.lib.utils.init_compendium import init_parsing
from command.lib.utils.permission import Permission
from command.lib.views.script_tree_view import ScriptTreeView
from command.models import init_database_connections


class FileAssignmentView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def change_associated_file_details(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        compendium = CompendiumDatabase.objects.get(id=comp_id)
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])

        assigned_file = AssignedFile.objects.using(compendium.compendium_nick_name).get(id=values['associated_file_id'])
        if values['field'] == 'script_name':
            assigned_file.script_name = values['value']
        elif values['field'] == 'parameters':
            assigned_file.parameters = values['value']
        elif values['field'] == 'order':
            assigned_file.order = values['value']
        elif values['field'] == 'input_filename':
            assigned_file.input_filename = values['value']
        assigned_file.save(using=compendium.compendium_nick_name)

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.PARSE_EXPERIMENT)
    def run_experiment_parsing_script(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        compendium = CompendiumDatabase.objects.get(id=comp_id)
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])

        scheduled_status = Status.objects.using(compendium.compendium_nick_name).get(name='entity_script_scheduled')
        for af in experiment.assignedfile_set.all():
            af.status = scheduled_status
            af.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id) + "_" + str(values['experiment_id'])).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        run_parsing_script.run_parsing_script.apply_async(
            (request.user.id, comp_id, values['experiment_id'], 'experiment',
             values['experiment_id'], channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.PARSE_EXPERIMENT)
    def run_platform_parsing_script(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        compendium = CompendiumDatabase.objects.get(id=comp_id)
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])
        scheduled_status = Status.objects.using(compendium.compendium_nick_name).get(name='entity_script_scheduled')
        platforms = []
        platform_ids = set()
        if isinstance(values['platform_id'], str) and values['platform_id'] == 'all':
            platform_ids = set([sample.platform_id for sample in experiment.sample_set.all()])
            platforms = Platform.objects.using(compendium.compendium_nick_name).filter(id__in=platform_ids)
        elif isinstance(values['platform_id'], list) and len(values['platform_id']) > 0:
            platforms = Platform.objects.using(compendium.compendium_nick_name).filter(id__in=values['platform_id'])
        for platform in platforms:
            platform_ids.add(platform.id)
            for af in platform.assignedfile_set.all():
                af.status = scheduled_status
                af.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id) + "_" + str(values['experiment_id'])).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        for platform_id in list(platform_ids):
            run_parsing_script.run_parsing_script.apply_async(
                (request.user.id, comp_id, values['experiment_id'], 'platform',
                platform_id, channel_name, view, operation)
            )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.PARSE_EXPERIMENT)
    def run_sample_parsing_script(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        compendium = CompendiumDatabase.objects.get(id=comp_id)
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])
        scheduled_status = Status.objects.using(compendium.compendium_nick_name).get(name='entity_script_scheduled')

        samples = []
        sample_ids = set()
        if isinstance(values['sample_id'], str) and values['sample_id'] == 'all':
            samples = experiment.sample_set.all()
        elif isinstance(values['sample_id'], list) and len(values['sample_id']) > 0:
            samples = Sample.objects.using(compendium.compendium_nick_name).filter(id__in=values['sample_id'])

        for sample in samples:
            sample_ids.add(sample.id)
            for af in sample.assignedfile_set.all():
                af.status = scheduled_status
                af.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id) + "_" + str(values['experiment_id'])).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        for sample_id in sample_ids:
            run_parsing_script.run_parsing_script.apply_async(
                (request.user.id, comp_id, values['experiment_id'], 'sample',
                sample_id, channel_name, view, operation)
            )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def run_assign_script(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        compendium = CompendiumDatabase.objects.get(id=comp_id)
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])

        script = values['assign_file_combobox']
        parameters = values['parameters']
        input_files = []
        base_dir = AdminOptions.objects.get(option_name='download_directory').option_value
        full_dir = os.path.join(base_dir, compendium.compendium_nick_name, experiment.experiment_access_id)
        if values['apply_to'] == 'all':
            files = glob.iglob(os.path.join(full_dir, '**', '*'), recursive=True)
            input_files = [filename for filename in files if os.path.isfile(filename)]
        elif values['apply_to'] == 'selected':
            input_files = [os.path.join(full_dir, filename) for filename in values['selected_files']
                           if os.path.isfile(os.path.join(full_dir, filename))]

        experiment_entity = (
            values['assign_file_combobox_exp'],
            None if not values['order_exp'] else values['order_exp'],
            values['parameters_exp']
        )
        platform_entity = (
            values['assign_file_combobox_plt'],
            None if not values['order_plt'] else values['order_plt'],
            values['parameters_plt']
        )
        sample_entity = (
            values['assign_file_combobox_smp'],
            None if not values['order_smp'] else values['order_smp'],
            values['parameters_smp']
        )

        run_file_assignment_script.run_file_assignment_script.apply_async(
            (request.user.id, comp_id, experiment.id, script, parameters, input_files,
             experiment_entity, platform_entity, sample_entity, channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def get_script_names(request, *args, **kwargs):
        return ScriptTreeView.get_script_names(request, args, kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DOWNLOAD_UPLOAD_EXPERIMENT)
    def upload_experiment_files(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        exp_id = int(req['values']['experiment_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)
        base_output_directory = AdminOptions.objects.get(option_name='download_directory')
        out_dir = os.path.join(base_output_directory.option_value, compendium.compendium_nick_name, experiment.experiment_access_id)

        os.makedirs(out_dir, exist_ok=True)

        file = request.FILES['experiment_data_file']
        full_path = os.path.join(out_dir, file.name)
        with open(full_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        uncompress_file.uncompress_file.apply_async(
            (request.user.id, comp_id, exp_id, file.name, channel_name, view, operation)
        )

        Group("compendium_" + str(compendium.id) + "_" + str(experiment.id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def remove_file_assignment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        view = request.POST['view']

        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])

        AssignedFile.objects.using(compendium.compendium_nick_name).get(id=values['assigned_file_id']).delete()

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def clean_file_assignment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        view = request.POST['view']

        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])
        entity_type = values['entity_type']

        if entity_type == 'ALL' or entity_type == 'EXP':
            AssignedFile.objects.using(compendium.compendium_nick_name). \
                filter(experiment=experiment).delete()
        if entity_type == 'ALL' or entity_type == 'PLT':
            platforms = list(set([sample.platform.id for sample in experiment.sample_set.all()]))
            AssignedFile.objects.using(compendium.compendium_nick_name).\
                filter(platform_id__in=platforms).delete()
        if entity_type == 'ALL' or entity_type == 'SMP':
            AssignedFile.objects.using(compendium.compendium_nick_name).\
                filter(sample__in=experiment.sample_set.all()).delete()

        Group("compendium_" + str(compendium.id) + "_" + str(experiment.id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DELETE_FILE)
    def delete_file(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        view = request.POST['view']

        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])
        base_dir = AdminOptions.objects.get(option_name='download_directory').option_value
        full_dir = os.path.join(base_dir, compendium.compendium_nick_name, experiment.experiment_access_id)

        for filename in values['files']:
            os.remove(os.path.join(full_dir, filename))

        Group("compendium_" + str(compendium.id) + "_" + str(experiment.id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def read_experiment_file(request, *args, **kwargs):
        path = request.GET['path']
        base_dir = AdminOptions.objects.get(option_name='download_directory').option_value

        try:
            with open(base_dir + path, 'r') as script_file:
                content = script_file.read()
        except Exception as e:
            with open(base_dir + path, 'rb') as script_file:
                content = script_file.read()
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Length'] = len(content)

        return response

    @staticmethod
    @forward_exception_to_http
    def get_experiment_files(request, *args, **kwargs):
        base_dir = AdminOptions.objects.get(option_name='download_directory').option_value
        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])
        init_database_connections()
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request.POST['values'])

        full_dir = os.path.join(base_dir, compendium.compendium_nick_name, experiment.experiment_access_id)

        files = glob.iglob(os.path.join(full_dir, '**', '*'), recursive=True)

        files = [{'name': os.path.basename(filename),
                  'path': filename.replace(base_dir, ''),
                  'type': os.path.splitext(filename)[1],
                  'date': time.strftime('%Y-%m-%d %H:%M', time.gmtime(os.path.getmtime(filename))),
                  'size': int(os.path.getsize(filename) / 1000)}
                 for filename in files if os.path.isfile(filename)]

        return HttpResponse(json.dumps({'success': True, 'files': files, 'total': len(files)}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_experiment_experiment_files(channel_name, view, request, user):
        channel = Channel(channel_name)

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request['values'])
        exp = experiment.to_dict()
        exp['status'] = Status.objects.using(compendium.compendium_nick_name). \
            get(name='entity_script_ready').to_dict()
        try:
            exp['status'] = experiment.assignedfile_set.all()[0].status.to_dict()
        except Exception as e:
            pass
        exp['parsing_details'] = [dict(list(assigned_file.to_dict().items()) +
                                       list({'status': exp['status']}.items()))
                                  for assigned_file in experiment.assignedfile_set.all()]

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'status': exp['status'],
                        'files': exp['parsing_details']
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    def read_reporter_platforms(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        view = request.POST['view']

        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['experiment_id'])

        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=values['platform_id'])
        platforms = [plt.to_dict() for plt in Platform.objects.using(compendium.compendium_nick_name).all()
                     if plt.biofeaturereporter_set.count() > 0]

        platforms.append(platform.to_dict())

        return HttpResponse(json.dumps({'success': True, 'platforms': platforms}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def change_reporter_platforms(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        view = request.POST['view']

        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])

        parsing_db = init_parsing(compendium.id, values['experiment_id'])
        parsing_plt = ParsingPlatform.objects.using(parsing_db).\
            get(platform_fk=values['platform_id'])
        try:
            Platform.objects.using(compendium.compendium_nick_name).get(
                id=values['reporter_platform_id']
            )
            parsing_plt.reporter_platform = values['reporter_platform_id']
        except Exception as e:
            pass
        parsing_plt.save(using=parsing_db)

        return HttpResponse(json.dumps({'success': True,}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_experiment_platform_files(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request['values'])
        parsing_db = init_parsing(request['compendium_id'], request['values'])
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = Platform.objects.using(compendium.compendium_nick_name). \
            filter(id__in=[s.platform.id for s in experiment.sample_set.all()]). \
            filter(Q(platform_name__contains=request['filter']) | Q(description__contains=request['filter'])
                   ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        platforms = []
        for platform in query_response:
            plt = platform.to_dict()
            reporter_platform_id = ParsingPlatform.objects.using(parsing_db).\
                get(platform_fk=platform.id).reporter_platform
            try:
                plt['reporter_platform'] = Platform.objects.using(compendium.compendium_nick_name).\
                    get(id=reporter_platform_id).platform_access_id
            except Exception as e:
                pass
            plt['status'] = Status.objects.using(compendium.compendium_nick_name). \
                get(name='entity_script_ready').to_dict()
            try:
                plt['status'] = platform.assignedfile_set.all()[0].status.to_dict()
            except Exception as e:
                pass
            plt['parsing_details'] = [assigned_file.to_dict() for assigned_file in platform.assignedfile_set.all()]
            platforms.append(plt)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'platforms': platforms,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_experiment_sample_files(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request['values'])
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = Sample.objects.using(compendium.compendium_nick_name).\
            filter(experiment=experiment).\
            filter(Q(sample_name__contains=request['filter']) | Q(description__contains=request['filter'])
                ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        samples = []
        for sample in query_response:
            smp = sample.to_dict()
            smp['status'] = Status.objects.using(compendium.compendium_nick_name).\
                get(name='entity_script_ready').to_dict()
            try:
                smp['status'] = sample.assignedfile_set.all()[0].status.to_dict()
            except Exception as e:
                pass
            smp['parsing_details'] = [assigned_file.to_dict() for assigned_file in sample.assignedfile_set.all()]
            samples.append(smp)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'samples': samples,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_experiment_files(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request['values'])
        base_dir = AdminOptions.objects.get(option_name='download_directory').option_value
        full_dir = os.path.join(base_dir, compendium.compendium_nick_name, experiment.experiment_access_id)

        files = glob.iglob(os.path.join(full_dir, '**', '*'), recursive=True)

        files = [{'name': os.path.basename(filename),
                  'path': filename.replace(base_dir, ''),
                  'type': os.path.splitext(filename)[1],
                  'date': time.strftime('%Y-%m-%d %H:%M', time.gmtime(os.path.getmtime(filename))),
                  'size': int(os.path.getsize(filename) / 1000)}
                 for filename in files if os.path.isfile(filename) and
                    request['filter'].lower() in os.path.basename(filename).lower()]

        ordering_value = request['ordering_value']
        ordering = request['ordering'] == 'DESC'
        if ordering_value in [k for x in files for k in x.keys()]:
            files.sort(key=lambda x: x[ordering_value], reverse=ordering)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'files': files[start:end],
                        'total': len(files)
                    }
                }
            })
        })

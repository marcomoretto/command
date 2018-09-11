import importlib
import json
import os
import shutil

from channels import Channel, Group
from django.db.models import Q, Count
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.experiment_search_result import ExperimentSearchResult
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http, check_permission
#from command.lib.utils.group_compendium_permission import GroupCompendiumPermission
from command.lib.utils.init_compendium import init_parsing
from command.lib.utils.permission import Permission
from command.models import init_database_connections


class ExperimentView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DELETE_FILE)
    def delete_downloaded_uploaded_data(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        base_dir = AdminOptions.objects.get(option_name='download_directory').option_value
        for exp_id in values:
            exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)
            full_dir = os.path.join(base_dir, compendium.compendium_nick_name, exp.experiment_access_id)
            try:
                shutil.rmtree(full_dir)
            except Exception as e:
                pass

        Group("compendium_" + str(comp_id)).send({
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
    @check_permission(Permission.DELETE_PARSING_DATA)
    def delete_parsing_data(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        for exp_id in values:
            parsing_db = init_parsing(compendium.id, exp_id, get_name_only=True)
            try:
                os.remove(parsing_db)
            except Exception as e:
                pass

        Group("compendium_" + str(comp_id)).send({
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
    @check_permission(Permission.DELETE_EXPERIMENT)
    def delete_experiment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        base_dir = AdminOptions.objects.get(option_name='download_directory').option_value
        for exp_id in values:
            exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)
            new_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_new')
            try:
                exp_search = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(
                    experiment_access_id=exp.experiment_access_id)
                exp_search.status = new_status
                exp_search.save(using=compendium.compendium_nick_name)
            except Exception as e:
                pass
            parsing_db = init_parsing(compendium.id, exp_id, get_name_only=True)
            try:
                os.remove(parsing_db)
            except Exception as e:
                pass
            try:
                full_dir = os.path.join(base_dir, compendium.compendium_nick_name, exp.experiment_access_id)
                shutil.rmtree(full_dir)
            except Exception as e:
                pass
            exp.delete()

        Group("compendium_" + str(comp_id)).send({
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
    @forward_exception_to_channel
    def read_experiment_sample_raw_data(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        sample = Sample.objects.using(compendium.compendium_nick_name).get(id=request['values']['id'])
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = sample.rawdata_set. \
            filter(Q(bio_feature_reporter__name__icontains=request['filter']) |
                   Q(value__contains=request['filter'])
                   ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        raw_data = []
        for rd in query_response:
            rd_dict = rd.to_dict(reduced=True)
            raw_data.append(rd_dict)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'raw_data': raw_data,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_sample_details(channel_name, view, request, user):
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
        query_response = Sample.objects.using(compendium.compendium_nick_name). \
            filter(experiment=experiment). \
            filter(Q(sample_name__icontains=request['filter']) |
                   Q(description__icontains=request['filter']) |
                   Q(platform__platform_access_id__icontains=request['filter'])
                   ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        samples = []

        for sample in query_response:
            smp = sample.to_dict()
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
    def read_experiments(*args, **kwargs):
        if type(args[0]) == str:
            return ExperimentView.read_experiments_channel(*args)
        else:
            return ExperimentView.read_experiments_http(args[0], args, kwargs)

    @staticmethod
    @forward_exception_to_http
    def read_experiments_http(request, *args, **kwargs):
        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])
        query_response = Experiment.objects.using(compendium.compendium_nick_name). \
            filter(Q(organism__icontains=request.POST['filter']) |
                   Q(experiment_access_id__icontains=request.POST['filter']) |
                   Q(scientific_paper_ref__icontains=request.POST['filter']) |
                   Q(description__icontains=request.POST['filter']) |
                   Q(experiment_name__icontains=request.POST['filter']))
        return HttpResponse(json.dumps({'success': True, 'ids': list(query_response.values_list('id', flat=True))}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_experiments_channel(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        #task_running = False
        operation = 'search_experiment_public_db'
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']
        #try:
        #    task_id = ViewTask.objects.using(compendium.compendium_nick_name).get(view=request['view'],
        #                                                                          operation=operation)
        #    task = AsyncResult(task_id.task_id)
        #    task_running = not task.ready()
        #except Exception as e:
        #    pass

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        exp_ids = set()
        # experiment
        init_database_connections()
        query_response = Experiment.objects.using(compendium.compendium_nick_name). \
            filter(Q(organism__icontains=request['filter']) |
                   Q(experiment_access_id__icontains=request['filter']) |
                   Q(scientific_paper_ref__icontains=request['filter']) |
                   Q(description__icontains=request['filter']) |
                   Q(experiment_name__icontains=request['filter'])).values_list('id', flat=True)
        exp_ids.update(query_response)
        # sample number
        query_response = Sample.objects.using(compendium.compendium_nick_name). \
            all().values('experiment').annotate(total=Count('id'))
        exp_ids.update([resp['experiment'] for resp in query_response if request['filter'] in str(resp['total'])])
        # platform access id
        platform_ids = Platform.objects.using(compendium.compendium_nick_name). \
            filter(Q(platform_access_id__icontains=request['filter'])).values_list('id', flat=True)
        query_response = Sample.objects.using(compendium.compendium_nick_name). \
            filter(platform_id__in=platform_ids).values_list('experiment_id', flat=True)
        exp_ids.update(query_response)

        ordererd = False
        query_response = Experiment.objects.using(compendium.compendium_nick_name). \
            filter(id__in=exp_ids)
        try:
            query_response.order_by(order + request['ordering_value'])[0]
            query_response = query_response.order_by(order + request['ordering_value'])
            ordererd = True
        except Exception as e:
            pass
        total = query_response.count()
        query_response = query_response[start:end]

        experiments = []
        for exp in query_response:
            e = exp.to_dict()
            e['status_description'] = exp.status.description
            if exp.status.name == 'experiment_excluded':
                e['description'] = 'EXCLUDED: ' + exp.comments + '. ' + e['description']
            module_name, class_name = '.'.join(exp.data_source.python_class.split('.')[:-1]), \
                exp.data_source.python_class.split('.')[-1]
            python_class = getattr(importlib.import_module(module_name), class_name)()
            e['experiment_accession_base_link'] = python_class.experiment_accession_base_link
            e['platform_accession_base_link'] = python_class.platform_accession_base_link
            e['scientific_paper_accession_base_link'] = python_class.scientific_paper_accession_base_link
            e['platforms'] = [plt.to_dict() for plt in Platform.objects.using(compendium.compendium_nick_name).distinct().filter(
                pk__in=set(exp.sample_set.values_list('platform_id', flat=True))
            )]
            e['n_samples'] = exp.sample_set.count()
            experiments.append(e)

        reverse = order == '-'

        if not ordererd:
            if request['ordering_value'] == 'platforms':
                experiments.sort(reverse=reverse, key=lambda x: ','.join(
                    [p['platform_access_id'] for p in x[request['ordering_value']]])
                                 )
            else:
                experiments.sort(reverse=reverse, key=lambda x: x[request['ordering_value']])

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'experiments': experiments,
                        #'task_running': task_running,
                        'total': total
                    }
                }
            })
        })

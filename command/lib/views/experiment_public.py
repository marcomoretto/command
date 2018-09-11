import importlib
import json

from celery.contrib.abortable import AbortableAsyncResult
from celery.result import AsyncResult

from command.lib.db.compendium.platform import Platform
from command.lib.utils.permission import Permission
from command.models import init_database_connections
from cport.celery import app
from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.experiment_search_result import ExperimentSearchResult
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.view_task import ViewTask
from command.lib.tasks import experiment_public
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http, check_permission


class ExperimentPublicView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DOWNLOAD_UPLOAD_EXPERIMENT)
    def exclude_experiment_public_db(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)
        for exp_id in values:
            excluded_status = Status.objects.using(compendium.compendium_nick_name).get(
                name='experiment_excluded')
            search_exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=exp_id)
            exp = Experiment(
                organism=search_exp.organism,
                experiment_access_id=search_exp.experiment_access_id,
                experiment_name=search_exp.experiment_name,
                scientific_paper_ref=search_exp.scientific_paper_ref,
                description=search_exp.description,
                comments=request.POST['message'],
                status=excluded_status,
                data_source=search_exp.data_source
            )
            exp.save(using=compendium.compendium_nick_name)
            Group("compendium_" + str(comp_id)).send({
                'text': json.dumps({
                    'stream': view,
                    'payload': {
                        'request': {'operation': 'refresh'},
                        'data': None
                    }
                })
            })
            Group("compendium_" + str(comp_id)).send({
                'text': json.dumps({
                    'stream': 'experiments',
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
    @check_permission(Permission.DOWNLOAD_UPLOAD_EXPERIMENT)
    def download_experiment_public_db(request, *args, **kwargs):
        init_database_connections()
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)
        for exp_id in values:
            scheduled_status = Status.objects.using(compendium.compendium_nick_name).get(
                name='experiment_scheduled')
            exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=exp_id)
            exp.status = scheduled_status
            exp.save(using=compendium.compendium_nick_name)
            experiment_public.experiment_public_download.apply_async(
                (request.user.id, comp_id, exp_id, channel_name, view, operation)
            )
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
    @check_permission(Permission.DOWNLOAD_UPLOAD_EXPERIMENT)
    def stop_search_experiment_public_db(request, *args, **kwargs):
        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']
        stop_operation = request.POST['values']
        compendium = CompendiumDatabase.objects.get(id=comp_id)
        try:
            view_task = ViewTask.objects.using(compendium.compendium_nick_name). \
                get(view=view, operation=stop_operation)
            abortable_async_result = AbortableAsyncResult(view_task.task_id)
            abortable_async_result.abort()
            view_task.delete()
            Group("compendium_" + str(comp_id)).send({
                'text': json.dumps({
                    'stream': view,
                    'payload': {
                        'request': {'operation': 'refresh'},
                        'data': None
                    }
                })
            })
        except Exception as e:
            pass

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DOWNLOAD_UPLOAD_EXPERIMENT)
    def search_experiment_public_db(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']
        taskid = experiment_public.experiment_public_search.apply_async(
            (request.user.id, comp_id, values['search_term'], values['source_id'],
             channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_experiment_search_results(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        task_running = False
        operation = 'search_experiment_public_db'
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']
        try:
            task_id = ViewTask.objects.using(compendium.compendium_nick_name).get(view=request['view'],
                                                                                  operation=operation)
            task = AsyncResult(task_id.task_id)
            task_running = not task.ready()
        except Exception as e:
            pass

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = ExperimentSearchResult.objects.using(compendium.compendium_nick_name). \
            filter(Q(organism__icontains=request['filter']) |
                   Q(experiment_access_id__icontains=request['filter']) |
                   Q(experiment_alternative_access_id__icontains=request['filter']) |
                   Q(platform__icontains=request['filter']) |
                   Q(scientific_paper_ref__icontains=request['filter']) |
                   Q(type__icontains=request['filter']) |
                   Q(description__icontains=request['filter']) |
                   Q(experiment_name__icontains=request['filter'])).order_by(
            order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        experiments = []
        for exp in query_response:
            e = exp.to_dict()
            module_name, class_name = '.'.join(exp.data_source.python_class.split('.')[:-1]), \
                                      exp.data_source.python_class.split('.')[-1]
            python_class = getattr(importlib.import_module(module_name), class_name)()
            e['experiment_accession_base_link'] = python_class.experiment_accession_base_link
            e['platform_accession_base_link'] = python_class.platform_accession_base_link
            e['scientific_paper_accession_base_link'] = python_class.scientific_paper_accession_base_link
            e['tag'] = ''
            if exp.platform:
                for plt_acc_id in exp.platform.split(';'):
                    try:
                        plt = Platform.objects.using(compendium.compendium_nick_name).\
                            get(platform_access_id=plt_acc_id)
                        if plt.biofeaturereporter_set.count() > 0:
                            e['tag'] = 'platform'
                    except Exception as exc:
                        pass
            try:
                already_present_exp = Experiment.objects.using(compendium.compendium_nick_name).\
                    get(experiment_access_id=exp.experiment_access_id)
                if already_present_exp.status.name == 'experiment_excluded':
                    e['tag'] = 'excluded'
                else:
                    e['tag'] = 'present'
                if e['status']['name'] != 'scheduled' and e['status']['name'] != 'experiment_downloading':
                    e['status'] = already_present_exp.status.to_dict()
            except Exception as exc:
                pass
            experiments.append(e)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'experiments': experiments,
                        'task_running': task_running,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_public_db(channel_name, view, request, user):
        channel = Channel(channel_name)

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        public_dbs = [db.to_dict() for db in DataSource.objects.\
            using(compendium.compendium_nick_name).filter(is_local=False)]

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'public_dbs': public_dbs,
                        'total': len(public_dbs)
                    }
                }
            })
        })

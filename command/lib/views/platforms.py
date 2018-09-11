import importlib
import json
import os
import time

import shutil

from celery.contrib.abortable import AbortableAsyncResult
from channels import Channel, Group

from command.lib.coll.platform.microarray_mapper import MicroarrayMapper
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.db.compendium.view_task import ViewTask
from command.lib.db.parsing.parsing_platform import ParsingPlatform
from command.lib.tasks import run_platform_mapper, import_platform_mapping
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http, check_permission
from command.lib.utils.init_compendium import init_parsing
from command.lib.utils.permission import Permission


class MicroarrayPlatformView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.REPORTER_MAPPING)
    def filter_alignment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        view = request.POST['view']
        channel_name = request.session['channel_name']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=values['platform_id'])

        base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
        plt_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                               'platforms', platform.platform_access_id)

        run_platform_mapper.run_alignment_filter.apply_async(
            (request.user.id, comp_id, plt_dir, values['platform_id'], values['alignment_id'],
             values['filter_params']['alignment_length_1'], values['filter_params']['gap_open_1'],
             values['filter_params']['mismatches_1'], values['filter_params']['alignment_length_2'],
             values['filter_params']['gap_open_2'], values['filter_params']['mismatches_2'],
             channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.REPORTER_MAPPING)
    def import_mapping(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        view = request.POST['view']
        channel_name = request.session['channel_name']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=values['platform_id'])
        blast_file_name = values['alignment_id']

        base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
        plt_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                               'platforms', platform.platform_access_id)

        import_platform_mapping.import_platform_mapping.apply_async(
            (request.user.id, comp_id, plt_dir, values['platform_id'], values['filter_id'],
             values['alignment_id'], channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")


    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.REPORTER_MAPPING)
    def delete_alignment_filter(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        view = request.POST['view']
        channel_name = request.session['channel_name']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)
        for del_operation in values['operations']:
            try:
                view_task = ViewTask.objects.using(compendium.compendium_nick_name). \
                    get(view=view, operation=del_operation)
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
        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=values['platform_id'])
        blast_file_name = values['alignment_id']

        base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
        plt_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                               'platforms', platform.platform_access_id)

        mapper = MicroarrayMapper(os.path.join(plt_dir, blast_file_name))
        mapper.delete_filter_db(values['filter_id'])

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
    @check_permission(Permission.REPORTER_MAPPING)
    def delete_alignment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        view = request.POST['view']
        channel_name = request.session['channel_name']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=values['platform_id'])

        base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
        plt_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                               'platforms', platform.platform_access_id)

        item_id = values['alignment_id'].replace('.blast', '')
        for file in [f for f in os.listdir(plt_dir) if
                     os.path.isfile(os.path.join(plt_dir, f)) and f.startswith(item_id)]:
            os.remove(os.path.join(plt_dir, file))

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
    @check_permission(Permission.REPORTER_MAPPING)
    def run_alignment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        view = request.POST['view']
        channel_name = request.session['channel_name']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=values['platform_id'])

        base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
        plt_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                               'platforms', platform.platform_access_id)
        os.makedirs(plt_dir, exist_ok=True)

        use_short_blastn = values.get('use_short_blastn', False)
        alignment_identity = float(values['alignment_identity'])

        run_platform_mapper.run_platform_mapper.apply_async(
            (request.user.id, comp_id, plt_dir, values['platform_id'],
             use_short_blastn, alignment_identity, channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def microarray_read_reporters(channel_name, view, request, user):
        pass

    @staticmethod
    @forward_exception_to_channel
    def read_mapping(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'

        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=request['values']['id'])
        base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
        plt_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                               'platforms', platform.platform_access_id)
        os.makedirs(plt_dir, exist_ok=True)

        blast_files = [f for f in os.listdir(plt_dir) if
                       os.path.isfile(os.path.join(plt_dir, f)) and f.endswith('.blast')]
        mappings = []
        for file in blast_files:
            mapper = MicroarrayMapper(os.path.join(plt_dir, file))
            parsing_details = mapper.get_filter_details()
            for pd in parsing_details:
                pd['alignment_id'] = file
            mappings.append(
                {
                    'id': file,
                    'date': time.strftime('%Y-%m-%d %H:%M', time.gmtime(os.path.getmtime(os.path.join(plt_dir, file)))),
                    'total_aligned': mapper.get_mapping_details()['total_aligned'],
                    'parsing_details': parsing_details,
                    'alignment_params': mapper.get_alignment_params(),
                    'status': mapper.get_alignment_status()
                }
            )
        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'mappings': mappings,
                        'total': len(mappings)
                    }
                }
            })
        })


class PlatformView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_channel
    def read_related_platforms(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        # platforms
        query_response = Sample.objects.using(compendium.compendium_nick_name).values_list(
            'platform__id',
            'reporter_platform__id'
        ).distinct()
        total = query_response.count()
        query_response = query_response[start:end]

        platforms = []
        for ppe in query_response:
            orig_plt = Platform.objects.using(compendium.compendium_nick_name).get(id=ppe[0])
            rep_plt = Platform.objects.using(compendium.compendium_nick_name).get(id=ppe[1])
            if orig_plt.biofeaturereporter_set.count() == 0:
                continue
            module_name, class_name = '.'.join(orig_plt.data_source.python_class.split('.')[:-1]), \
                                      orig_plt.data_source.python_class.split('.')[-1]
            orig_plt_python_class = getattr(importlib.import_module(module_name), class_name)()
            module_name, class_name = '.'.join(rep_plt.data_source.python_class.split('.')[:-1]), \
                                      rep_plt.data_source.python_class.split('.')[-1]
            rep_plt_python_class = getattr(importlib.import_module(module_name), class_name)()
            exp_id = list(Sample.objects.using(compendium.compendium_nick_name).\
                filter(platform__id=ppe[0], reporter_platform__id=ppe[1]).\
                values_list('experiment_id', flat=True).distinct())
            exp_links = []
            exp = []
            for eid in exp_id:
                e = Experiment.objects.using(compendium.compendium_nick_name).get(id=eid)
                module_name, class_name = '.'.join(e.data_source.python_class.split('.')[:-1]), \
                                          e.data_source.python_class.split('.')[-1]
                exp_python_class = getattr(importlib.import_module(module_name), class_name)()
                exp_links.append(exp_python_class.experiment_accession_base_link)
                exp.append(e.experiment_access_id)
            p = {
                'original_platform': orig_plt.platform_access_id,
                'reporter_platform': rep_plt.platform_access_id,
                'experiments': exp,
                'original_platform_local': False,
                'reporter_platform_local': False,
                'original_platform_accession_base_link': orig_plt_python_class.platform_accession_base_link,
                'reporter_platform_accession_base_link': rep_plt_python_class.platform_accession_base_link,
                'experiment_accession_base_links': exp_links
            }
            platforms.append(p)

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
    @forward_exception_to_http
    @check_permission(Permission.DELETE_PLATFORM)
    def delete_platform(request, *args, **kwargs):
        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=request.POST['values'])
        for exp_id in platform.platform.get_queryset().values_list('experiment_id', flat=True).distinct():
            parsing_db = init_parsing(compendium.id, exp_id)
            try:
                ParsingPlatform.objects.using(parsing_db).get(platform_fk=platform.id).delete()
            except Exception as e:
                pass
        platform.delete()

        base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
        plt_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                               'platforms', platform.platform_access_id)
        shutil.rmtree(plt_dir, ignore_errors=True)

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
    def read_platforms(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        # platforms
        query_response = Platform.objects.using(compendium.compendium_nick_name). \
            filter(Q(platform_name__icontains=request['filter']) |
                   Q(description__icontains=request['filter']) |
                   Q(platform_access_id__icontains=request['filter'])).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        platforms = []
        for plt in query_response:
            p = plt.to_dict()
            module_name, class_name = '.'.join(plt.data_source.python_class.split('.')[:-1]), \
                plt.data_source.python_class.split('.')[-1]
            python_class = getattr(importlib.import_module(module_name), class_name)()
            p['platform_accession_base_link'] = python_class.platform_accession_base_link
            #experiments = set()
            #n_samples = 0
            #n_samples_imported = 0
            #for smp in plt.platform.get_queryset().all():
            #    if smp.rawdata_set.count() > 0:
            #        n_samples_imported += 1
            #    experiments.add(smp.experiment_id)
            #p['n_experiments'] = len(experiments)
            #p['n_samples'] = n_samples
            #p['n_samples_imported'] = n_samples_imported
            platforms.append(p)

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

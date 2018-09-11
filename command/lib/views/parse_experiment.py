import json

from channels import Channel, Group
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.platform_type import PlatformType
from command.lib.db.parsing.parsing_bio_feature_reporter import ParsingBioFeatureReporter
from command.lib.db.parsing.parsing_experiment import ParsingExperiment
from command.lib.db.parsing.parsing_platform import ParsingPlatform
from command.lib.db.parsing.parsing_raw_data import ParsingRawData
from command.lib.db.parsing.parsing_sample import ParsingSample
from command.lib.tasks import import_experiment
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http, check_permission
#from command.lib.utils.group_compendium_permission import GroupCompendiumPermission
from command.lib.utils.init_compendium import init_parsing
from command.lib.utils.permission import Permission


class ParseExperimentView(View):

    def get(self, request, operation, exp_id, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, exp_id, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.IMPORT_EXPERIMENT)
    @check_permission(Permission.PARSE_EXPERIMENT)
    def import_experiment(request, *args, **kwargs):
        exp_id = request.POST['values']

        keep_platform = request.POST.get('keep_platform', False) == 'true'

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        import_experiment.import_experiment.apply_async(
            (request.user.id, comp_id, exp_id, keep_platform, channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.IMPORT_PLATFORM)
    @check_permission(Permission.PARSE_EXPERIMENT)
    def import_experiment_platform(request, *args, **kwargs):
        exp_id = request.POST['values']

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        import_experiment.import_experiment_platform.apply_async(
            (request.user.id, comp_id, exp_id, channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.PARSE_EXPERIMENT)
    def remove_experiment_channel(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        channel = Channel(channel_name)
        view = request.POST['view']
        if comp_id:
            compendium = CompendiumDatabase.objects.get(id=comp_id)
            Group("compendium_" + str(compendium.id) + "_" + str(values)).discard(channel)

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_parse_experiment_preview_bio_feature_reporter(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        parsing_db = init_parsing(request['compendium_id'], request['values']['experiment_id'])
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        platform = ParsingPlatform.objects.using(parsing_db).get(id=request['values']['id'])
        imported_platform = Platform.objects.using(compendium.compendium_nick_name).get(id=platform.platform_fk)
        # bio features
        is_imported = imported_platform.biofeaturereporter_set.count() > 0
        parsed = platform.parsingbiofeaturereporter_set.count() > 0
        if is_imported and not parsed:
            query_response = BioFeatureReporter.objects.using(compendium.compendium_nick_name). \
                filter(platform=imported_platform).filter(Q(name__icontains=request['filter']) |
                                                 Q(description__icontains=request['filter'])).order_by(
                order + request['ordering_value'])
            total = query_response.count()
            query_response = query_response[start:end]

            bio_feature_reporter = []
            for bfr in query_response:
                b = bfr.to_dict()
                for field in bfr.biofeaturereportervalues_set.all():
                    b[field.bio_feature_reporter_field.name] = field.value
                bio_feature_reporter.append(b)
        else:
            query_response = ParsingBioFeatureReporter.objects.using(parsing_db). \
                filter(platform=platform).filter(Q(name__icontains=request['filter']) |
                                                 Q(description__icontains=request['filter'])).order_by(
                order + request['ordering_value'])
            total = query_response.count()
            query_response = query_response[start:end]

            bio_feature_reporter = []
            for bfr in query_response:
                b = bfr.to_dict()
                for field in bfr.parsingbiofeaturereportervalues_set.all():
                    b[field.bio_feature_reporter_field] = field.value
                bio_feature_reporter.append(b)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'bio_feature_reporter': bio_feature_reporter,
                        'imported': is_imported and not parsed,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_parse_experiment_preview_raw_data(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        parsing_db = init_parsing(request['compendium_id'], request['values']['experiment_id'])
        parsing_sample = ParsingSample.objects.using(parsing_db).get(id=request['values']['id'])
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = ParsingRawData.objects.using(parsing_db). \
            filter(sample=parsing_sample). \
            filter(Q(bio_feature_reporter_name__contains=request['filter']) |
                   Q(value__contains=request['filter'])
                   ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        raw_data = []
        status = 'ready'
        for rd in query_response:
            rd_dict = rd.to_dict()
            raw_data.append(rd_dict)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'raw_data': raw_data,
                        'status': status,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_platform_preview(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        parsing_db = init_parsing(request['compendium_id'], request['values'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request['values'])
        parsing_experiment = ParsingExperiment.objects.using(parsing_db).get(experiment_fk=experiment.id)
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        platform_ids = list(set([sample.platform_id for sample in parsing_experiment.parsingsample_set.all()]))
        query_response = ParsingPlatform.objects.using(parsing_db). \
            filter(id__in=platform_ids). \
            filter(Q(platform_name__contains=request['filter']) |
                   Q(description__contains=request['filter']) |
                   Q(platform_access_id__contains=request['filter'])
                   ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        platforms = []
        status = 'importing' if experiment.status.name == 'experiment_raw_data_importing' else None
        for platform in query_response:
            imported_platform = Platform.objects.using(compendium.compendium_nick_name).get(id=platform.platform_fk)
            if not status and imported_platform.status:
                status = 'importing' if imported_platform.status.name == 'platform_importing' else None
            plt = platform.to_dict()
            plt['experiment_id'] = experiment.id
            plt['reporter_platform'] = ''
            plt['is_imported'] = imported_platform.biofeaturereporter_set.count() > 0
            try:
                p_type = PlatformType.objects.using(compendium.compendium_nick_name). \
                    get(name=plt['platform_type'])
                plt['bio_feature_reporter_name'] = p_type.bio_feature_reporter_name
                plt['bio_features_reporter_fields'] = [
                    field.to_dict() for field in p_type.biofeaturereporterfields_set.all()
                ]
            except Exception as e:
                pass
            platforms.append(plt)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'platforms': platforms,
                        'status': status,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_sample_preview(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])
        parsing_db = init_parsing(request['compendium_id'], request['values'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request['values'])
        parsing_experiment = ParsingExperiment.objects.using(parsing_db).get(experiment_fk=experiment.id)
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = ParsingSample.objects.using(parsing_db). \
            filter(experiment=parsing_experiment). \
            filter(Q(sample_name__contains=request['filter']) |
                   Q(description__contains=request['filter']) |
                   Q(platform__platform_access_id__contains=request['filter'])
                   ).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        samples = []
        status = 'importing' if experiment.status.name == 'experiment_raw_data_importing' else None
        if not status:
            for smp in experiment.sample_set.all():
                if smp.platform.status and smp.platform.status.name == 'platform_importing':
                    status = 'importing'
        for sample in query_response:
            smp = sample.to_dict()
            smp['experiment_id'] = experiment.id
            smp['reporter_platform'] = Platform.objects.using(compendium.compendium_nick_name).\
                    get(id=sample.reporter_platform).to_dict()
            samples.append(smp)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'samples': samples,
                        'status': status,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_experiment(channel_name, view, request, user):
        channel = Channel(channel_name)

        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])

        Group("compendium_" + str(compendium.id) + "_" + str(request['values'])).add(channel)

        parsing_db = init_parsing(request['compendium_id'], request['values'])
        experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=request['values'])
        parsing_experiment = ParsingExperiment.objects.using(parsing_db).get(experiment_fk=request['values'])
        n_samples = parsing_experiment.parsingsample_set.all().count()
        platforms = ",".join(list(set(
                [sample.platform.platform_access_id for sample in parsing_experiment.parsingsample_set.all()]
            )))
        status = 'importing' if experiment.status.name == 'experiment_raw_data_importing' else None
        if not status:
            for smp in experiment.sample_set.all():
                if smp.platform.status and smp.platform.status.name == 'platform_importing':
                    status = 'importing'

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'status': status,
                        'experiment': experiment.to_dict(),
                        'parsing_experiment': parsing_experiment.to_dict(),
                        'platforms': platforms,
                        'n_samples': n_samples
                    }
                }
            })
        })
import importlib
import json
import os

from channels import Channel, Group
from django.db.models import Q, Count
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.experiment_search_result import ExperimentSearchResult
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.tasks import parse_bio_feature_file
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http, check_permission
from command.lib.utils.permission import Permission


class BioFeatureGeneView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.ADD_BIOFEATURE)
    def upload_bio_feature_file(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        base_output_directory = AdminOptions.objects.get(option_name='download_directory')
        out_dir = os.path.join(base_output_directory.option_value, compendium.compendium_nick_name, 'bio_feature')

        os.makedirs(out_dir, exist_ok=True)

        file = request.FILES['file_name']
        full_path = os.path.join(out_dir, file.name)
        with open(full_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        parse_bio_feature_file.run_parsing_bio_feature.apply_async(
            (request.user.id, comp_id, full_path, req['bio_feature_name'], req['values']['file_type'],
             channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")


class BioFeatureView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DELETE_BIOFEATURE)
    def delete_bio_features(request, *args, **kwargs):
        comp_id = request.POST['compendium_id']
        view = request.POST['view']
        channel_name = request.session['channel_name']
        operation = request.POST['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        BioFeature.objects.using(compendium.compendium_nick_name).all().delete()

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
    def read_bio_feature(channel_name, view, request, user):
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
        # bio features
        query_response = BioFeature.objects.using(compendium.compendium_nick_name). \
            filter(Q(name__icontains=request['filter']) |
                   Q(description__icontains=request['filter'])).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        bio_feature = []
        for bf in query_response:
            b = bf.to_dict()
            for field in bf.biofeaturevalues_set.all():
                b[field.bio_feature_field.name] = field.value
            bio_feature.append(b)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'bio_feature': bio_feature,
                        'total': total
                    }
                }
            })
        })

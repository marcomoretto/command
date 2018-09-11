import json
import os

from channels import Channel, Group
from django.db.models import Q, Count
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.experiment_search_result import ExperimentSearchResult
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.tasks import parse_bio_feature_file
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http


class BioFeatureReporterView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_channel
    def read_bio_feature_reporter(channel_name, view, request, user):
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
        # bio features
        query_response = BioFeatureReporter.objects.using(compendium.compendium_nick_name). \
            filter(platform=platform).filter(Q(name__icontains=request['filter']) |
                   Q(description__icontains=request['filter'])).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        bio_feature_reporter = []
        for bfr in query_response:
            b = bfr.to_dict()
            for field in bfr.biofeaturereportervalues_set.all():
                b[field.bio_feature_reporter_field.name] = field.value
            bio_feature_reporter.append(b)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'bio_feature_reporter': bio_feature_reporter,
                        'total': total
                    }
                }
            })
        })

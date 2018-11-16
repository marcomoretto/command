import json
import os

from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.anno.annotation_parser import BaseAnnotationParser
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_annotation import BioFeatureAnnotation
from command.lib.db.compendium.ontology import Ontology
from command.lib.tasks import annotation
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http, check_permission
from command.lib.utils.message import Message
from command.lib.utils.permission import Permission


class BioFeatureAnnoView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DELETE_BIO_FEATURE_ANNOTATION)
    def delete_bio_feature_annotation(request, *args, **kwargs):
        req = request.POST

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        BioFeatureAnnotation.objects.using(compendium.compendium_nick_name).all().delete()

        message = Message(type='info', title='Annotation', message='Biological feature annotation has been deleted')
        message.send_to(Channel(channel_name))

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
    @check_permission(Permission.IMPORT_BIO_FEATURE_ANNOTATION)
    def upload_bio_feature_annotation(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        base_output_directory = AdminOptions.objects.get(option_name='download_directory')
        out_dir = os.path.join(base_output_directory.option_value, compendium.compendium_nick_name, 'bio_feature_annotation')

        os.makedirs(out_dir, exist_ok=True)
        filename = None
        file_type = None
        if 'file_name' in request.FILES:
            file = request.FILES['file_name']
            filename = os.path.join(out_dir, file.name)
            file_type = req['values']['file_type']
            with open(filename, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        annotation.annotation_task.apply_async(
            (request.user.id, comp_id, req['values']['ontology'],
             filename, file_type, channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def get_file_type(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        file_type = [{'file_type': c.FILE_TYPE_NAME} for c in BaseAnnotationParser.get_parser_classes()]
        return HttpResponse(json.dumps({'success': True, 'file_type': file_type}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def get_ontologies(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ontologies = {}
        if values['destination'] == 'bio_feature':
            ontologies = list(Ontology.objects.using(compendium.compendium_nick_name).\
                filter(is_biofeature=True).values('id', 'name'))

        return HttpResponse(json.dumps({'success': True, 'ontologies': ontologies}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_bio_feature_anno(channel_name, view, request, user):
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
            b['annotation'] = []
            for bfa in bf.biofeatureannotation_set.all():
                ontology = bfa.ontology_node.ontology
                node = bfa.ontology_node
                ann = node.to_dict()
                ann['ontology'] = ontology.to_dict()
                ann['columns'] = ontology.json['columns']
                ann['fields'] = node.json
                b['annotation'].append(ann)
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


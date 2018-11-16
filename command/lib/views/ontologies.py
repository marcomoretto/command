import json
import os

from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.anno.ontology_helper import OntologyHelper
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.ontology import Ontology
from command.lib.db.compendium.ontology_edge import OntologyEdge
from command.lib.db.compendium.ontology_node import OntologyNode
from command.lib.tasks import ontology
from command.lib.utils.decorators import forward_exception_to_http, forward_exception_to_channel, check_permission
from command.lib.utils.permission import Permission


class OntologiesView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_channel
    def read_ontology_nodes(channel_name, view, request, user):
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])

        ontology = Ontology.objects.using(compendium.compendium_nick_name).get(id=request['values']['ontology_id'])
        if request['values']['text']:
            query_response = OntologyNode.objects.using(compendium.compendium_nick_name).filter(
                Q(ontology=ontology) &
                Q(original_id__icontains=request['values']['text'])
            )
        else:
            query_response = OntologyNode.objects.using(compendium.compendium_nick_name).filter(
                Q(ontology=ontology)
            )[:100]
        query_response = query_response
        total = query_response.count()
        nodes = []
        for g in query_response:
            gg = g.to_dict()
            gg['valid'] = True
            nodes.append(gg)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'nodes': nodes,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def get_ontology_nodes(channel_name, view, request, user):
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])

        values = None
        ontology_id = 0
        ontology = None
        if 'values' in request:
            values = json.loads(request['values'])
            ontology_id = values['ontology_id']
            ontology = Ontology.objects.using(compendium.compendium_nick_name).get(id=ontology_id)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'

        ordering_value = request['ordering_value']
        if ordering_value not in list(OntologyNode().__dict__.keys()):
            ordering_value = 'id'
        query_response = OntologyNode.objects.using(compendium.compendium_nick_name).filter(
            Q(ontology_id=ontology_id)&
            (Q(id__icontains=request['filter'])|
             Q(original_id__icontains=request['filter'])|
             Q(json__icontains=request['filter']))) \
            .order_by(order + ordering_value)
        total = query_response.count()
        query_response = query_response[start:end]

        columns = ontology.json['columns'] if ontology and ontology.json and 'columns' in ontology.json else []
        nodes = []
        for g in query_response:
            gg = g.to_dict()
            for c in columns:
                if c['data_index'] not in g.json:
                    continue
                if type(g.json[c['data_index']]) == list:
                    gg[c['data_index']] = ' '.join(g.json[c['data_index']])
                else:
                    gg[c['data_index']] = g.json[c['data_index']]
            nodes.append(gg)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'nodes': nodes,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    @check_permission(Permission.ONTOLOGIES)
    def read_ontologies(channel_name, view, request, user):
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = Ontology.objects.using(compendium.compendium_nick_name).filter(Q(name__icontains=request['filter'])) \
            .order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        ontologies = [g.to_dict(columns=True) for g in query_response]

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'ontologies': ontologies,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.MODIFY_ONTOLOGY)
    def delete_ontology_node(request, *args, **kwargs):
        node_id = request.POST['values']
        comp_id = request.POST['compendium_id']
        view = request.POST['view']

        compendium = CompendiumDatabase.objects.get(id=comp_id)
        node = OntologyNode.objects.using(compendium.compendium_nick_name).get(id=node_id)
        node.delete(using=compendium.compendium_nick_name)

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")


    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.MODIFY_ONTOLOGY)
    def create_ontology_node(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        new_node = OntologyNode()
        new_node.ontology_id = req['values']['id']
        new_node.original_id = req['values']['original_id']
        node_json = dict(req['values'])
        del node_json['original_id']
        del node_json['id']
        del node_json['parent_node_id']
        del node_json['edge_type']
        del node_json['parents_id_tagfield']
        if 'edge_directed' in node_json:
            del node_json['edge_directed']
        for k, v in node_json.items():
            s = v.split(',')
            if len(s) > 1:
                node_json[k] = s
        new_node.json = node_json
        new_node.save(using=compendium.compendium_nick_name)

        for parent_id in req['values']['parents_id_tagfield']:
            try:
                parent_node = OntologyNode.objects.using(compendium.compendium_nick_name).get(
                    Q(ontology_id=req['values']['id']) &
                    Q(id=parent_id)
                )
                new_edge = OntologyEdge()
                new_edge.ontology_id = req['values']['id']
                new_edge.source = parent_node
                new_edge.target = new_node
                new_edge.is_directed = True
                new_edge.edge_type = 'is_a'
                new_edge.save(using=compendium.compendium_nick_name)
            except Exception as e:
                pass

        return HttpResponse(json.dumps({'success': True}),
                     content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.MODIFY_ONTOLOGY)
    def update_ontology_node(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        channel_name = request.session['channel_name']
        view = req['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        node = OntologyNode.objects.using(compendium.compendium_nick_name).get(id=req['values']['node_id'])
        node.original_id = req['values']['original_id']
        node_json = dict(req['values'])
        del node_json['original_id']
        del node_json['node_id']
        del node_json['id']
        del node_json['parent_node_id']
        del node_json['edge_type']
        del node_json['parents_id_tagfield']
        if 'edge_directed' in node_json:
            del node_json['edge_directed']
        for k, v in node_json.items():
            s = v.split(',')
            if len(s) > 1:
                node_json[k] = s
        node.json = node_json
        node.save(using=compendium.compendium_nick_name)

        for parent_id in req['values']['parents_id_tagfield']:
            try:
                parent_node = OntologyNode.objects.using(compendium.compendium_nick_name).get(
                    Q(ontology_id=req['values']['id']) &
                    Q(id=parent_id)
                )
                OntologyEdge.objects.using(compendium.compendium_nick_name).filter(target=node).delete()
                new_edge = OntologyEdge()
                new_edge.ontology_id = req['values']['id']
                new_edge.source = parent_node
                new_edge.target = node
                new_edge.is_directed = True
                new_edge.edge_type = 'is_a'
                new_edge.save(using=compendium.compendium_nick_name)
            except Exception as e:
                pass

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def get_ontology_node_details(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        on = OntologyNode.objects.using(compendium.compendium_nick_name).get(id=values)
        node = {**on.to_dict(), **on.json}
        for edge in OntologyEdge.objects.using(compendium.compendium_nick_name).filter(target=on):
            if 'parents_id_tagfield' not in node:
                node['parents_id_tagfield'] = []
            parent = edge.source.to_dict()
            parent['valid'] = True
            node['parents_id_tagfield'].append(parent)

        return HttpResponse(json.dumps({'success': True, 'node': node}),
                            content_type="application/json")


    @staticmethod
    @forward_exception_to_http
    def get_ontology_columns(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ontology = Ontology.objects.using(compendium.compendium_nick_name).get(id=values['ontology_id'])
        ontology_help = OntologyHelper(compendium.compendium_nick_name, ontology.name)

        columns = [{"text": c.title().replace('_', ' '), "data_index": c} for c in list(OntologyNode().to_dict().keys())]
        if ontology.json and 'columns' in ontology.json:
            columns = ontology.json['columns'] + columns

        return HttpResponse(json.dumps({'success': True, 'columns': columns}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DELETE_ONTOLOGY)
    def delete_ontology(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ontology = Ontology.objects.using(compendium.compendium_nick_name).get(id=values)
        ontology.delete(using=compendium.compendium_nick_name)

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
    @check_permission(Permission.MODIFY_ONTOLOGY)
    def update_ontology(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ontology = Ontology.objects.using(compendium.compendium_nick_name).get(id=req['values']['id'])
        ontology.name = req['values']['name']
        ontology.description = req['values']['description']
        ontology.is_biofeature = 'biofeature' in req['values']['destination']
        ontology.is_sample = 'sample' in req['values']['destination']
        ontology.json = {'columns': req['values']['fields']}
        ontology.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(compendium.id)).send({
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
    @check_permission(Permission.CREATE_ONTOLOGY)
    def create_ontology(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        base_output_directory = AdminOptions.objects.get(option_name='download_directory')
        out_dir = os.path.join(base_output_directory.option_value, compendium.compendium_nick_name, 'ontology')

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
        fields_json = {'columns': req['values']['fields']}
        ontology.create_ontology_task.apply_async(
            (request.user.id, comp_id, req['values']['name'],
             req['values']['description'], req['values']['destination'], fields_json,
             filename, file_type, channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def get_ontology_structure(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        node_id = values.get('node_id', None)
        ontology = Ontology.objects.using(compendium.compendium_nick_name).get(id=values['ontology_id'])
        ontology_help = OntologyHelper(compendium.compendium_nick_name, ontology.name)
        ontology_structure = ontology_help.get_neighbourhood(node_id, level=1)

        return HttpResponse(json.dumps({'success': True, 'ontology': ontology_structure}),
                            content_type="application/json")

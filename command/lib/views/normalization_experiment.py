import json

from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.normalization import Normalization
from command.lib.db.compendium.normalization_design_group import NormalizationDesignGroup
from command.lib.db.compendium.normalization_design_sample import NormalizationDesignSample
from command.lib.db.compendium.normalization_experiment import NormalizationExperiment
from command.lib.db.compendium.normalization_type import NormalizationType
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http


class NormalizationExperimentView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_channel
    def read_normalization_design_group(channel_name, view, request, user):
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
        query_response = NormalizationDesignGroup.objects.using(compendium.compendium_nick_name).filter(
            Q(name__icontains=request['filter'])).order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        ndgs = []
        for norm in query_response:
            n = norm.to_dict()
            n['samples'] = [{
                'id': k.id,
                'sample_name': k.sample.sample_name,
                'description': k.sample.description
            } for k in norm.normalizationdesignsample_set.all()]
            ndgs.append(n)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'normalization_design_group': ndgs,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    def delete_sample_from_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        nds = NormalizationDesignSample.objects.using(compendium.compendium_nick_name).get(id=values)
        ndg = nds.normalization_design
        ndg.design['elements']['nodes'] = [node for node in ndg.design['elements']['nodes'] if
                                           str(node['data']['id']) != str(values)]
        ndg.design['elements']['edges'] = [edge for edge in ndg.design['elements']['edges'] if
                                           str(edge['data']['target']) != str(values) and str(edge['data']['source']) != str(values)]

        nds.delete(using=compendium.compendium_nick_name)
        ndg.save(using=compendium.compendium_nick_name)

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
    def update_sample_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ndg = NormalizationDesignGroup.objects.using(compendium.compendium_nick_name).get(id=values['group_id'])
        ndg.name = values['group_name']
        ndg.save(using=compendium.compendium_nick_name)

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
    def update_node_positions(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ndg = NormalizationDesignGroup.objects.using(compendium.compendium_nick_name).get(id=values['normalization_experiment_id'])
        for node_pos in values['node_positions']:
            n = [node for node in ndg.design['elements']['nodes'] if str(node['data']['id']) == node_pos['node_id']][0]
            n['position'] = node_pos['position']
        ndg.save(using=compendium.compendium_nick_name)

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def delete_condition_sample_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ndg = NormalizationDesignGroup.objects.using(compendium.compendium_nick_name).get(id=values['normalization_experiment_id'])
        for condition_id in values['condition_id']:
            ndg.design['elements']['nodes'] = [node for node in ndg.design['elements']['nodes'] if
                                               node['data']['type'] != 'condition' or
                                               str(node['data']['id']) != str(condition_id)]
            ndg.design['elements']['edges'] = [edge for edge in ndg.design['elements']['edges'] if
                                               str(edge['data']['target']) != str(condition_id) and str(
                                                   edge['data']['source']) != str(condition_id)]
        ndg.save(using=compendium.compendium_nick_name)

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def create_condition_sample_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        samples = NormalizationDesignSample.objects.using(compendium.compendium_nick_name).filter(id__in=values['samples'])
        ndg = samples[0].normalization_design

        parent_node_id = 'parent_' + '_'.join(values['samples'])
        ndg.design['elements']['nodes'].append({
            'data': {
                'id': parent_node_id,
                'name': values['condition_name'],
                'type': 'condition'
            }
        })
        for node in ndg.design['elements']['nodes']:
            if str(node['data']['id']) in values['samples']:
                node['data']['parent'] = parent_node_id

        ndg.save(using=compendium.compendium_nick_name)

        return HttpResponse(json.dumps({'success': True, 'design': ndg.design}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def remove_normalization_design_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ndg = NormalizationDesignGroup.objects.using(compendium.compendium_nick_name).get(id=values)
        ndg.delete(using=compendium.compendium_nick_name)

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
    def select_design_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ndg = NormalizationDesignGroup.objects.using(compendium.compendium_nick_name).get(id=values)

        return HttpResponse(json.dumps({'success': True, 'design': ndg.design}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def create_sample_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ndg = NormalizationDesignGroup()
        ndg.name = values['group_name']
        ndg.normalization_experiment_id = values['normalization_experiment_id']
        ndg.save(using=compendium.compendium_nick_name)

        samples = []
        for sample_id in values['samples']:
            nds = NormalizationDesignSample()
            nds.normalization_design = ndg
            nds.sample_id = sample_id
            samples.append(nds)
        NormalizationDesignSample.objects.using(compendium.compendium_nick_name).bulk_create(samples)

        json_elements = {
            'elements': {
                'nodes': [],
                'edges': []
            }
        }
        for s in ndg.normalizationdesignsample_set.all():
            json_elements['elements']['nodes'].append({
                'data': {
                    'id': s.id,
                    'name': s.sample.sample_name,
                    'type': 'sample'
                }
            })
        ndg.design = json_elements
        ndg.save(using=compendium.compendium_nick_name)

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
    def get_experiment_details(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ne = NormalizationExperiment.objects.using(compendium.compendium_nick_name).get(id=values)

        return HttpResponse(json.dumps({'success': True, 'normalization_experiment': ne.to_dict()}),
                            content_type="application/json")
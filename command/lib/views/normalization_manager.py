import json

from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.normalization import Normalization
from command.lib.db.compendium.normalization_experiment import NormalizationExperiment
from command.lib.db.compendium.normalization_type import NormalizationType
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http, check_permission
from command.lib.utils.permission import Permission


class NormalizationManagerView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_channel
    @check_permission(Permission.NORMALIZATION_MANAGER)
    def read_experiments(channel_name, view, request, user):
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=request['compendium_id'])

        if 'values' in request and request['values']['text']:
            query_response = Experiment.objects.using(compendium.compendium_nick_name).filter(
                Q(experiment_access_id__icontains=request['values']['text'])
            )
        else:
            query_response = Experiment.objects.using(compendium.compendium_nick_name).all()[:100]
        query_response = query_response
        total = query_response.count()
        exps = []
        for e in query_response:
            ex = e.to_dict()
            ex['valid'] = True
            ex['experiment_access_id_extended'] = e.experiment_access_id + ' - ' + e.experiment_name
            exps.append(ex)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'experiments': exps,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.MODIFY_NORMALIZATION)
    def update_use_experiment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ne = NormalizationExperiment.objects.using(compendium.compendium_nick_name).get(id=values['normalization_experiment_id'])
        ne.use_experiment = values['checked']
        ne.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': 'normalization',
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
    @check_permission(Permission.MODIFY_NORMALIZATION)
    def remove_experiment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        ne = NormalizationExperiment.objects.using(compendium.compendium_nick_name).get(id=values)
        ne.delete(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh', 'values': ne.normalization_id},
                    'data': None
                }
            })
        })
        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': 'normalization',
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
    @check_permission(Permission.MODIFY_NORMALIZATION)
    def remove_all_experiment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        norm = Normalization.objects.using(compendium.compendium_nick_name).get(id=values)
        norm.normalizationexperiment_set.all().delete()

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh', 'values': values},
                    'data': None
                }
            })
        })
        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': 'normalization',
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
    @check_permission(Permission.MODIFY_NORMALIZATION)
    def add_all_experiment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        norm = Normalization.objects.using(compendium.compendium_nick_name).get(id=values)
        nes = []
        included = norm.normalizationexperiment_set.values_list('experiment_id', flat=True)
        all = Experiment.objects.using(compendium.compendium_nick_name).all().values_list('id', flat=True)
        todo = set(all) - set(included)
        for exp_id in todo:
            ne = NormalizationExperiment()
            ne.normalization_id = values
            ne.experiment_id = exp_id
            nes.append(ne)
        NormalizationExperiment.objects.using(compendium.compendium_nick_name).bulk_create(nes)

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': 'normalization',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh', 'values': norm.id},
                    'data': None
                }
            })
        })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.MODIFY_NORMALIZATION)
    def add_experiment(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = values['compendium_id']
        channel_name = request.session['channel_name']
        view = values['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        norm = Normalization.objects.using(compendium.compendium_nick_name).get(id=values['values']['id'])
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=values['values']['experiment'])
        if norm.normalizationexperiment_set.filter(experiment_id=values['values']['experiment']).count() == 0:
            ne = NormalizationExperiment()
            ne.normalization = norm
            ne.experiment = exp
            ne.save(using=compendium.compendium_nick_name)

            Group("compendium_" + str(comp_id)).send({
                'text': json.dumps({
                    'stream': 'normalization',
                    'payload': {
                        'request': {'operation': 'refresh'},
                        'data': None
                    }
                })
            })
            Group("compendium_" + str(comp_id)).send({
                'text': json.dumps({
                    'stream': view,
                    'payload': {
                        'request': {'operation': 'refresh', 'values': norm.id},
                        'data': None
                    }
                })
            })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DELETE_NORMALIZATION)
    def remove_normalization(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        view = request.POST['view']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        norm = Normalization.objects.using(compendium.compendium_nick_name).get(id=values)
        norm.delete(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh', 'values': norm.id},
                    'data': None
                }
            })
        })

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': 'normalization',
                'payload': {
                    'request': {'operation': 'refresh', 'values': norm.id},
                    'data': None
                }
            })
        })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.MODIFY_NORMALIZATION)
    def update_normalization(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        norm = Normalization.objects.using(compendium.compendium_nick_name).get(id=req['values']['normalization_id'])
        norm.name = req['values']['name']
        norm.is_public = 'is_public' in req['values'] and req['values']['is_public'] == '1'
        norm.normalization_type_id = req['values']['normalization_type']
        norm.version = req['values']['version']
        norm.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': 'normalization',
                'payload': {
                    'request': {'operation': 'refresh', 'values': norm.id},
                    'data': None
                }
            })
        })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")


    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.CREATE_NORMALIZATION)
    def create_normalization(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        norm = Normalization()
        norm.name = req['values']['name']
        norm.is_public = 'is_public' in req['values'] and req['values']['is_public'] == '1'
        norm.normalization_type_id = req['values']['normalization_type']
        norm.version = req['values']['version']
        norm.save(using=compendium.compendium_nick_name)

        Group("compendium_" + str(comp_id)).send({
            'text': json.dumps({
                'stream': 'normalization',
                'payload': {
                    'request': {'operation': 'refresh', 'values': norm.id},
                    'data': None
                }
            })
        })

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def get_normalization_type(request, *args, **kwargs):
        compendium = CompendiumDatabase.objects.get(id=request.POST['compendium_id'])
        types = [nt.to_dict() for nt in NormalizationType.objects.using(compendium.compendium_nick_name).all()]

        return HttpResponse(json.dumps({'success': True, 'normalization_type': types}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    @check_permission(Permission.NORMALIZATION_MANAGER)
    def read_normalization_experiments(channel_name, view, request, user):
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

        experiments = []
        total = 0
        try:
            normalization_id = 0 if 'values' not in request else request['values']
            normalization = Normalization.objects.using(compendium.compendium_nick_name).get(id=normalization_id)
            query_response = normalization.normalizationexperiment_set.filter(
                (Q(experiment__experiment_access_id__icontains=request['filter']))|
                (Q(experiment__experiment_name__icontains=request['filter']))) \
                .order_by(order + request['ordering_value'])
            total = query_response.count()
            query_response = query_response[start:end]

            for exp in query_response:
                experiments.append(exp.to_dict())
        except Exception as e:
            pass

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'normalization_experiments': experiments,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    @check_permission(Permission.NORMALIZATION_MANAGER)
    def read_normalizations(channel_name, view, request, user):
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
        query_response = Normalization.objects.using(compendium.compendium_nick_name).filter(
            (Q(name__icontains=request['filter']))|
            (Q(normalization_type__name__icontains=request['filter']))) \
            .order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        normalizations = []
        for norm in query_response:
            n = norm.to_dict()
            n['n_exp'] = norm.normalizationexperiment_set.filter(use_experiment=True).count()
            normalizations.append(n)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'normalizations': normalizations,
                        'total': total
                    }
                }
            })
        })


import importlib
import inspect
import json
import os
import pkgutil

from channels import Channel, Group
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

import command.consumers

from command.lib.anno.base_parser import BaseParser
from command.lib.coll.biological_feature import importers
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.admin.compendium_type import CompendiumType
from command.lib.db.compendium.bio_feature_fields import BioFeatureFields
from command.lib.utils import init_compendium
from command.lib.utils.database import get_database_list, create_db
from command.lib.utils.decorators import forward_exception_to_channel, forward_exception_to_http
from command.lib.utils.message import Message
from command.models import init_database_connections

import copy
from django.contrib.auth.models import Group as UserGroup


class CompendiumManagerView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def update_compendium_type(request, *args, **kwargs):
        raise DeprecationWarning("Deprecated")
        values = json.loads(request.POST['values'])
        c_type = CompendiumType(id=values['id'])
        c_type.name = values['name']
        c_type.description = values['description']
        c_type.save()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group('admin').send({
            'text': json.dumps({
                'stream': 'compendia',
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
    def create_compendium_type(request, *args, **kwargs):
        raise DeprecationWarning("Deprecated")
        values = json.loads(request.POST['values'])
        c_type = CompendiumType(name=values['name'],
                                description=values['description'])
        c_type.save()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group('admin').send({
            'text': json.dumps({
                'stream': 'compendia',
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
    def delete_compendium_type(request, *args, **kwargs):
        raise DeprecationWarning("Deprecated")
        c_type = CompendiumType(id=request.POST['values'])
        c_type.delete()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        Group('admin').send({
            'text': json.dumps({
                'stream': 'compendia',
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    def read_compendium_types(*args, **kwargs):
        if type(args[0]) == str:
            return CompendiumManagerView.read_compendium_types_channel(*args)
        else:
            return CompendiumManagerView.read_compendium_types_http(args[0], args, kwargs)

    @staticmethod
    @forward_exception_to_http
    def read_compendium_types_http(request, *args, **kwargs):
        query_response = CompendiumType.objects.filter(Q(name__contains=request.POST['filter']) |
                                                      Q(description__contains=request.POST['filter']))
        return HttpResponse(json.dumps({'success': True, 'ids': list(query_response.values_list('id', flat=True))}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_compendium_types_channel(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']
        c_types = []
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = CompendiumType.objects.filter(Q(name__contains=request['filter']) |
                                             Q(description__contains=request['filter'])).order_by(
            order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        for ct in query_response:
            c_types.append(ct.to_dict())

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'compendium_types': c_types,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    def init_compendium(request, *args, **kwargs):
        init_compendium.init_compendium(request.POST['values'])
        init_database_connections()
        msg = Message(type='info', title='Compendium initialized', message='Compendium successfully initialized')
        return HttpResponse(json.dumps(msg.to_dict()),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def update_compendium(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        db = CompendiumDatabase(id=values['id'])
        db.compendium_name = values['compendium_name']
        db.compendium_nick_name = values['compendium_nick_name']
        db.description = values['description']
        db.html_description = values['html_description']
        db.compendium_type = CompendiumType.objects.get(id=values['compendium_type'])
        db.db_engine = values['db_engine']
        db.db_user = values.get('db_user', None)
        db.db_password = values.get('db_password', None)
        db.db_port = values.get('db_port', None)
        db.db_host = values.get('db_host', None)
        db.save()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
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
    def delete_compendium(request, *args, **kwargs):
        id = request.POST['values']
        compendium = CompendiumDatabase.objects.get(id=id)
        compendium.delete()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        channel_name = request.session['channel_name']
        channel = Channel(channel_name)
        Group("compendium_" + str(id)).discard(channel)
        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def get_db_list(request, *args, **kwargs):
        dbs = get_database_list()
        return HttpResponse(json.dumps({'success': True, 'dbs': dbs}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def create_compendium(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        db = CompendiumDatabase()
        db.compendium_name = values['compendium_name']
        db.compendium_nick_name = values['compendium_nick_name']
        db.description = values['description']
        db.html_description = values['html_description']
        db.compendium_type = CompendiumType.objects.get(id=values['compendium_type'])
        db.db_engine = values['db_engine']
        db.db_user = values.get('db_user', None)
        db.db_password = values.get('db_password', None)
        db.db_port = values.get('db_port', None)
        db.db_host = values.get('db_host', None)
        if values['create_db']:
            admin_db = copy.copy(db)
            admin_db.compendium_nick_name = values['admin']['username']
            admin_db.db_user = values['admin']['username']
            admin_db.db_password = values['admin']['password']
            create_db(values['admin']['username'], admin_db.get_setting_entry()[1], db.compendium_nick_name, db.db_user)
        db.save()
        init_database_connections()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        channel_name = request.session['channel_name']
        channel = Channel(channel_name)
        Group("compendium_" + str(db.id)).add(channel)
        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    def read_compendia(*args, **kwargs):
        if type(args[0]) == str:
            return CompendiumManagerView.read_compendia_channel(*args)
        else:
            return CompendiumManagerView.read_compendia_http(args[0], args, kwargs)

    @staticmethod
    @forward_exception_to_http
    def read_compendia_http(request, *args, **kwargs):
        query_response = CompendiumDatabase.objects.filter(Q(compendium_name__contains=request.POST['filter']) |
                                                           Q(compendium_nick_name__contains=request.POST['filter']) |
                                                           Q(description__contains=request.POST['filter']) |
                                                           Q(html_description__contains=request.POST['filter']))
        return HttpResponse(json.dumps({'success': True, 'ids': list(query_response.values_list('id', flat=True))}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_compendia_channel(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = CompendiumDatabase.objects.filter(Q(compendium_name__contains=request['filter']) |
                                                           Q(compendium_nick_name__contains=request['filter']) |
                                                           Q(description__contains=request['filter']) |
                                                           Q(html_description__contains=request['filter'])).order_by(
            order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        compendia = []
        importe_mapping_file_types = []
        ontology_file_types = BaseParser.get_parser_classes()

        permitted_db = command.consumers.GroupCompendiumPermission.get_permitted_db(user)
        for db in query_response:
            if not user.is_staff and not user.is_superuser and db.compendium_nick_name not in permitted_db:
                continue
            compendium = db.to_dict()
            try:
                compendium['bio_features_fields'] = [bff.to_dict() for bff in
                                                     BioFeatureFields.objects.using(db.compendium_nick_name).all()]
                importe_mapping_file_types = [{'file_type': cls.FILE_TYPE_NAME} for cls in importers.importer_mapping[db.compendium_type.bio_feature_name]]
                ontology_file_types = [{"file_type": cls.FILE_TYPE_NAME} for cls in ontology_file_types]
            except Exception as e:
                pass
            compendium['ontology_file_types'] = ontology_file_types
            compendium['bio_feature_file_types'] = importe_mapping_file_types
            compendia.append(compendium)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'compendia': compendia,
                        'total': total
                    }
                }
            })
        })

import json
from urllib.parse import urlparse

import requests
from channels import Channel, Group
from django.contrib.auth.models import Group as UserGroup
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.views import View

import command.consumers
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.utils.decorators import forward_exception_to_http, forward_exception_to_channel


class UserGroupManagerView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def create_group(request, *args, **kwargs):
        group = UserGroup(name=request.POST['values'])
        group.save()
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
    def delete_group(request, *args, **kwargs):
        group = UserGroup.objects.get(id=request.POST['values'])
        group.delete()
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
    def update_group(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        group = UserGroup.objects.get(id=values['id'])
        group.name = values['name']
        group.save()
        Group('admin').send({
            'text': json.dumps({
                'stream': request.POST['view'],
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        return HttpResponse(json.dumps({'success': True}), content_type="application/json")

    @staticmethod
    @forward_exception_to_channel
    def read_groups(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']
        fields = ['id', 'name']

        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = UserGroup.objects.filter(Q(name__contains=request['filter'])) \
            .order_by(order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]

        groups = [{k: g.__dict__[k] for k in fields} for g in query_response]

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'groups': groups,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    def update_user(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        user = User.objects.get(id=values['id'])
        user.username = values['username']
        user.first_name = values['first_name']
        user.last_name = values['last_name']
        user.email = values['email']
        user.is_active = 'active' in values and values['active'] == 'on'
        user.is_staff = 'admin' in values and values['admin'] == 'on'
        user.is_superuser = 'admin' in values and values['admin'] == 'on'
        if 'reset_password' in values and values['reset_password'] == 'on':
            user.set_password(user.username)
        user.save()
        # groups
        for g in UserGroup.objects.all():
            g.user_set.remove(user)
        if 'group_id' in values:
            if type(values['group_id']) == list:
                for group_id in values['group_id']:
                    group = UserGroup.objects.get(id=group_id)
                    group.user_set.add(user)
            else:
                group = UserGroup.objects.get(id=values['group_id'])
                group.user_set.add(user)

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
    def create_user(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        new_user = User()
        new_user.username = values['username']
        new_user.first_name = values['first_name']
        new_user.last_name = values['last_name']
        new_user.email = values['email']
        new_user.is_active = 'active' in values and values['active'] == 'on'
        new_user.is_staff = 'admin' in values and values['admin'] == 'on'
        new_user.is_superuser = 'admin' in values and values['admin'] == 'on'
        new_user.set_password(new_user.username)
        new_user.save()
        # groups
        if 'group_id' in values:
            if type(values['group_id']) == list:
                for group_id in values['group_id']:
                    group = UserGroup.objects.get(id=group_id)
                    group.user_set.add(new_user)
            else:
                group = UserGroup.objects.get(id=values['group_id'])
                group.user_set.add(new_user)

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
    def delete_user(request, *args, **kwargs):
        user = User.objects.get(id=request.POST['values'])
        user.delete()
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
    @forward_exception_to_channel
    def read_users(channel_name, view, request, user):
        channel = Channel(channel_name)

        start = 0
        end = None
        if request['page_size']:
            start = (request['page'] - 1) * request['page_size']
            end = start + request['page_size']
        users = []
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'is_active',
                  'is_superuser']
        order = ''
        if request['ordering'] == 'DESC':
            order = '-'
        query_response = User.objects.filter(Q(username__contains=request['filter']) |
                                             Q(first_name__contains=request['filter']) |
                                             Q(last_name__contains=request['filter']) |
                                             Q(email__contains=request['filter'])).order_by(
            order + request['ordering_value'])
        total = query_response.count()
        query_response = query_response[start:end]
        for u in query_response:
            user = {k: u.__dict__[k] for k in fields if k != 'last_login' and k != 'date_joined'}
            if u.__dict__['last_login']:
                user['last_login'] = u.__dict__['last_login'].strftime('%Y-%m-%d %H:%M')
            if u.__dict__['date_joined']:
                user['date_joined'] = u.__dict__['date_joined'].strftime('%Y-%m-%d %H:%M')
            user['user_groups'] = [{'id': g.id, 'name': g.name} for g in u.groups.all()]
            users.append(user)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'users': users,
                        'total': total
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_channel
    def read_privileges(channel_name, view, request, user):
        channel = Channel(channel_name)

        if 'values' in request:
            req = json.loads(request['values'])
            group_permissions = UserGroup.objects.get(id=req['group_id']).permissions.all()
            db = CompendiumDatabase.objects.get(id=req['compendium_id'])
            selected = [gc.codename for gc in group_permissions.filter(content_type__app_label=db.compendium_nick_name)]
            permissions = command.consumers.GroupCompendiumPermission.get_all_permissions(selected)
        else:
            permissions = command.consumers.GroupCompendiumPermission.get_all_permissions()

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'privileges': permissions,
                        'total': len(permissions)
                    }
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    def update_group_privileges(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        group = UserGroup.objects.get(id=values['group_id'])
        db = CompendiumDatabase.objects.get(id=values['compendium_id'])
        for permission_codename in values['permission_codename']:
            permission = command.consumers.GroupCompendiumPermission.get_permission(
                permission_codename,
                db
            )
            if values['select']:
                group.permissions.add(permission)
            else:
                group.permissions.remove(permission)
                permission.delete()

        return HttpResponse(json.dumps({'success': True}), content_type="application/json")

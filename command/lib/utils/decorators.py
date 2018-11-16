import functools
import json

from channels import Channel
from django.db import ProgrammingError
from django.http import HttpResponse
import traceback

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.utils.message import Message


def forward_exception_to_http(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = Message(type='error', title='Error', message=str(e) + '<br>' + traceback.format_exc())
            return HttpResponse(json.dumps(error_msg.to_dict()),
                                content_type="application/json")
    return func_wrapper


def forward_exception_to_channel(func):
    def func_wrapper(*args, **kwargs):
        channel_name, view, request, user = args
        channel = Channel(channel_name)
        try:
            func(*args, **kwargs)
        except ProgrammingError as e:
            error_msg = Message(type='error', title='Error', message=str(e) + "<br><br> Is the compendium initialized?")
            error_msg.send_to(channel)
        except Exception as e:
            error_msg = Message(type='error', title='Error', message=str(e))
            error_msg.send_to(channel)
    return func_wrapper


def check_permission(perm_codename):
    def _check_permission(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            request = args[0]
            if type(request) == str:
                user = args[-1]
                request = args[-2]
                comp_id = request['compendium_id']
            else:
                user = request.user
                if 'compendium_id' in request.POST:
                    comp_id = request.POST['compendium_id']
                else:
                    comp_id = json.loads(request.POST['request'])['compendium_id']
            if user.is_staff and user.is_superuser:
                return func(*args, **kwargs)
            compendium = CompendiumDatabase.objects.get(id=comp_id)
            for g in user.groups.all():
                for p in g.permissions.all():
                    if p.content_type.app_label == compendium.compendium_nick_name and p.codename == perm_codename:
                        return func(*args, **kwargs)
            error_msg = Message(type='permission_error', title='', message='')
            return HttpResponse(json.dumps(error_msg.to_dict()),
                                content_type="application/json")
        return func_wrapper
    return _check_permission
import json
import os
from os.path import isfile, isdir

from channels import Channel, Group
from django.http import HttpResponse
from django.views import View

from command.lib import parsing_scripts
from command.lib.utils import file_system
from command.lib.utils.decorators import forward_exception_to_http, forward_exception_to_channel, check_permission
from command.lib.utils.permission import Permission


class ScriptTreeView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def get_script_names(request, *args, **kwargs):
        values = request.POST['values']

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']

        base_path = os.path.dirname(parsing_scripts.__file__)
        sub_dirs = [d for d in os.listdir(base_path) if isdir(os.path.join(base_path, d))]
        all = {}
        for sub_dir in sub_dirs:
            full_path = os.path.join(base_path, sub_dir)
            onlyfiles = [{'script_name': f} for f in os.listdir(full_path) if
                         isfile(os.path.join(full_path, f)) and f != '__init__.py']
            all[sub_dir] = onlyfiles
        result = all.get(values, all)

        return HttpResponse(json.dumps({'success': True, 'data': result}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.USE_PYTHON_EDITOR)
    def update_script_file(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']

        base_path = os.path.dirname(parsing_scripts.__file__)
        old_file_name = base_path + values['path']
        new_file_name = os.path.join(os.path.dirname(old_file_name), values['file_name'])
        if not new_file_name.endswith('.py'):
            new_file_name += '.py'
        os.rename(old_file_name, new_file_name)
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
    @check_permission(Permission.USE_PYTHON_EDITOR)
    def delete_script_file(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']

        base_path = os.path.dirname(parsing_scripts.__file__)
        full_path = base_path + values['file_name']
        os.remove(full_path)
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
    @check_permission(Permission.USE_PYTHON_EDITOR)
    def create_script_file(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']

        base_path = os.path.dirname(parsing_scripts.__file__)
        full_path = base_path + values['path']
        if os.path.isfile(full_path):
            full_path = os.path.dirname(full_path)
        file_name = values['file_name']
        if not file_name.endswith('.py'):
            file_name += '.py'
        full_path = os.path.join(full_path, file_name)
        open(full_path, 'a').close()
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
    @check_permission(Permission.USE_PYTHON_EDITOR)
    def save_script(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        base_path = os.path.dirname(parsing_scripts.__file__)
        full_path = base_path + values['file_name']
        source = values['source']
        with open(full_path, 'w') as script_file:
            script_file.write(source)
        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

    @staticmethod
    @forward_exception_to_http
    def read_script_file(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        base_path = os.path.dirname(parsing_scripts.__file__)
        full_path = base_path + values['file_name']

        with open(full_path, 'r') as script_file:
            data = script_file.read()

        return HttpResponse(json.dumps({'success': True, 'data': data}),
                            content_type="application/json")


    @staticmethod
    @forward_exception_to_channel
    def read_script_tree(channel_name, view, request, user):
        channel = Channel(channel_name)

        path = os.path.dirname(parsing_scripts.__file__)
        path_hierarchy = file_system.path_hierarchy(path, base_path=path, name_filter=request['filter']) # get only subdirectories
        path_hierarchy = [d for d in path_hierarchy['children'] if not d['leaf']] # without files
        path_hierarchy.append({'leaf': True, 'path': '/README', 'text': 'README'})
        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': path_hierarchy
                }
            })
        })

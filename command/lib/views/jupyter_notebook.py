import json
import os
import shutil

import requests
from channels import Channel, Group
from django.http import HttpResponse
from django.views import View

from command.lib import parsing_scripts
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.utils import file_system
from command.lib.utils.decorators import forward_exception_to_http, forward_exception_to_channel
import urllib.parse
from cport import settings


class JupyterNotebookView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_channel
    def read_notebook_tree(channel_name, view, request, user):
        channel = Channel(channel_name)

        path = os.path.join(
                os.path.dirname(os.path.realpath(__name__)),
                'notebook'
        )

        path_hierarchy = file_system.path_hierarchy(path, base_path=path,
                                                    name_filter=request['filter'])  # get only subdirectories
        path_hierarchy = [d for d in path_hierarchy['children'] if not d['leaf'] or (d['leaf'] and d['text'].endswith('.ipynb'))]  # without files
        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': path_hierarchy
                }
            })
        })

    @staticmethod
    @forward_exception_to_http
    def update_notebook_file_folder(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']

        full_path = os.path.join(
            os.path.dirname(os.path.realpath(__name__)),
            'notebook'
        )
        old_file_name = full_path + values['path']
        new_file_name = os.path.join(os.path.dirname(old_file_name), values['file_name'])
        if values['type'] == 'notebook' and not new_file_name.endswith('.ipynb'):
            new_file_name += '.ipynb'
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
    def delete_notebook_file_folder(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']

        full_path = os.path.join(
            os.path.dirname(os.path.realpath(__name__)),
            'notebook'
        )
        full_path = full_path + values['file_name']
        if values['type'] == 'folder':
            shutil.rmtree(full_path)
        else:
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
    def create_notebook_file_folder(request, *args, **kwargs):
        values = json.loads(request.POST['values'])
        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']

        full_path = os.path.join(
                os.path.dirname(os.path.realpath(__name__)),
                'notebook'
        )
        if 'path' in values:
            full_path = full_path + values['path']
        full_path = os.path.join(full_path, values['file_name'])
        if values['type'] == 'folder':
            os.makedirs(full_path, exist_ok=True)
        else:
            if not full_path.endswith('.ipynb'):
                full_path += '.ipynb'
            with open(full_path, 'a') as f:
                f.write('''
                    {
                     "cells": [],
                     "metadata": {},
                     "nbformat": 4,
                     "nbformat_minor": 2
                    }
                ''')
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
    def get_notebook_ip(request, *args, **kwargs):
        token = settings.JUPYTER_TOKEN

        jupyter_notebook_ip = AdminOptions.objects.get(option_name='jupyter_notebook_ip').option_value
        values = json.loads(request.POST.get('values', '{"path": "/README.ipynb"}'))
        jupyter_notebook_ip = '/'.join([jupyter_notebook_ip, 'notebooks' + values['path'] + '?token=' + token])

        return HttpResponse(json.dumps({'success': True,
                                        'jupyter_notebook_ip': jupyter_notebook_ip}),
                            content_type="application/json")

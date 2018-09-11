import json
import os
import shutil

from channels import Channel, Group
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.utils.decorators import forward_exception_to_http, forward_exception_to_channel


class AdminOptionsView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def clear_admin_options_directory(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        item = list(values.items())[0]
        path = os.path.expanduser(item[1])
        os.makedirs(path, exist_ok=True)
        for root, dirs, files in os.walk(path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

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
    def update_admin_options_directory(request, *args, **kwargs):
        values = json.loads(request.POST['values'])

        item = list(values.items())[0]
        path = os.path.expanduser(item[1])
        os.makedirs(path, exist_ok=True)
        AdminOptions.objects.filter(option_name=item[0]).delete()
        option = AdminOptions(option_name=item[0], option_value=path)
        option.save()

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
    def read_admin_options(channel_name, view, request, user):
        channel = Channel(channel_name)

        channel.send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': request,
                    'data': {
                        'admin_options': [o.to_dict() for o in AdminOptions.objects.all()]
                    }
                }
            })
        })

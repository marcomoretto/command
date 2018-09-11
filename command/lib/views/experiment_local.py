import json
import os

import yaml
from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.tasks import experiment_local
from command.lib.utils.decorators import forward_exception_to_http, check_permission
from command.lib.utils.permission import Permission


class ExperimentLocalView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.DOWNLOAD_UPLOAD_EXPERIMENT)
    def upload_experiment_files(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        channel_name = request.session['channel_name']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        exp_id = req['values']['experiment_id']
        exp_name = ''
        exp_descr = ''
        exp_structure_file = req['values']['experiment_structure_file']
        base_output_directory = AdminOptions.objects.get(option_name='download_directory')
        out_dir = os.path.join(base_output_directory.option_value, compendium.compendium_nick_name, exp_id)

        os.makedirs(out_dir, exist_ok=True)

        file = request.FILES['experiment_data_file']
        full_path = os.path.join(out_dir, file.name)
        with open(full_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        experiment_local.experiment_local_upload.apply_async(
            (request.user.id, comp_id, exp_id, exp_name, exp_descr, exp_structure_file, file.name, channel_name, view, operation)
        )

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")


    @staticmethod
    @forward_exception_to_http
    #@check_permission(GroupCompendiumPermission.DOWNLOAD_UPLOAD_EXPERIMENT)
    def upload_experiment_structure_file(request, *args, **kwargs):
        req = json.loads(request.POST['request'])

        comp_id = req['compendium_id']
        view = req['view']
        operation = req['operation']
        compendium = CompendiumDatabase.objects.get(id=comp_id)

        exp_id = req['values']['experiment_id']
        base_output_directory = AdminOptions.objects.get(option_name='download_directory')
        out_dir = os.path.join(base_output_directory.option_value, compendium.compendium_nick_name, exp_id)

        os.makedirs(out_dir, exist_ok=True)

        file = request.FILES['experiment_structure_file']

        full_path = os.path.join(out_dir, file.name)
        with open(full_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        with open(full_path) as f:
            yaml.load(f)

        return HttpResponse(json.dumps({'success': True}),
                            content_type="application/json")

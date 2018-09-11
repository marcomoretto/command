import csv
import json
import os
import io, gzip

from django.http import HttpResponse
from django.views import View

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.raw_data import RawData
from command.lib.tasks import export_data
from command.lib.utils.decorators import forward_exception_to_http, check_permission
#from command.lib.utils.group_compendium_permission import GroupCompendiumPermission
from command.lib.utils.message import Message
from command.lib.utils.permission import Permission


class ExportDataView(View):

    def get(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    def post(self, request, operation, *args, **kwargs):
        method = getattr(self, operation)
        return method(request, *args, **kwargs)

    @staticmethod
    @forward_exception_to_http
    def read_file(request, *args, **kwargs):
        path = request.GET['path']
        base_dir = AdminOptions.objects.get(option_name='raw_data_directory').option_value

        if not os.path.isfile(base_dir + path):
            return HttpResponse('File ' + os.path.basename(path) + ' no longer exists!',
                                    content_type='text/plain')
        file = open(base_dir + path, 'rb')
        if path.endswith('tsv.gz'):
            response = HttpResponse(file.read(), content_type='application/x-gzip')
            response['Content-Disposition'] = 'attachment; filename="raw_data.tsv.gz"'
        elif path.endswith('hdf5'):
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="raw_data.hdf5"'
        response['Content-Length'] = str(os.stat(base_dir + path).st_size)

        return response

    @staticmethod
    @forward_exception_to_http
    @check_permission(Permission.EXPORT_COMPENDIUM)
    def export_raw_data(request, *args, **kwargs):
        comp_id = request.POST['compendium_id']
        channel_name = request.session['channel_name']
        view = request.POST['view']
        operation = request.POST['operation']

        compendium = CompendiumDatabase.objects.get(id=comp_id)

        base_dir = AdminOptions.objects.get(option_name='raw_data_directory').option_value
        full_dir = os.path.join(base_dir, compendium.compendium_nick_name, 'export_raw_data')

        # check genes, raw_data and mapping
        bio_features_check = BioFeature.objects.using(compendium.compendium_nick_name).count() > 0
        raw_data_check = RawData.objects.using(compendium.compendium_nick_name).count() > 0
        mapping_check = BioFeatureReporter.objects.using(compendium.compendium_nick_name).\
            exclude(bio_feature__isnull=True).count() > 0

        if bio_features_check and raw_data_check and mapping_check:
            export_data.export_raw_data.apply_async(
                (request.user.id, comp_id, full_dir, channel_name, view, operation)
            )
            return HttpResponse(json.dumps({'success': True}),
                                content_type="application/json")
        else:
            error_msg = Message(type='error', title='Cannot export data',
                                message='To export data you need to:'
                                        '<ul>'
                                        '<li>import biological features;</li>'
                                        '<li>import at least one experiment;</li>'
                                        '<li>platform mapped (if requested);</li>'
                                        '</ul>')
            return HttpResponse(json.dumps(error_msg.to_dict()),
                                content_type="application/json")

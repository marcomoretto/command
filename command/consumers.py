import json
import collections

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.utils.permission import Permission as CommandPermission
from command.lib.views.admin_options_view import AdminOptionsView
from command.lib.views.bio_feature import BioFeatureView, BioFeatureGeneView
from command.lib.views.bio_feature_anno import BioFeatureAnnoView
from command.lib.views.bio_feature_reporter import BioFeatureReporterView
from command.lib.views.compendium_manager import CompendiumManagerView
from command.lib.views.experiment_public import ExperimentPublicView
from command.lib.views.experiments import ExperimentView
from command.lib.views.export_data import ExportDataView
from command.lib.views.file_assignment import FileAssignmentView
from command.lib.views.jupyter_notebook import JupyterNotebookView
from command.lib.views.message_log import MessageLogView
from command.lib.views.normalization_experiment import NormalizationExperimentView
from command.lib.views.normalization_manager import NormalizationManagerView
from command.lib.views.ontologies import OntologiesView
from command.lib.views.parse_experiment import ParseExperimentView
from command.lib.views.platforms import PlatformView, MicroarrayPlatformView
from command.lib.views.script_tree_view import ScriptTreeView
from command.lib.views.test import TestView
from command.lib.views.user_group_manager import UserGroupManagerView


class Dispatcher:
    dispatcher = {
        AdminOptionsView: ['admin_options'],
        UserGroupManagerView: ['_users', 'users', 'groups', 'privileges', 'user_group_manager'],
        CompendiumManagerView: ['_compendia', 'compendia', 'compendium_types', 'compendia_manager'],
        ExperimentPublicView: ['_experiment_public', 'experiment_public', 'window_new_experiment'],
        ExperimentView: ['experiments', 'window_experiment_sample_details'],
        PlatformView: ['platform_manager', 'platforms', 'related_platforms'],
        MicroarrayPlatformView: ['microarray_platforms', 'window_map_microarray_platform'],
        BioFeatureView: ['bio_feature'],
        BioFeatureAnnoView: ['bio_feature_anno', 'bio_feature_annotation', 'window_import_bio_feature_annotation'],
        BioFeatureGeneView: ['bio_feature_gene', 'window_import_gene_bio_features'],
        BioFeatureReporterView: ['bio_feature_reporter'],
        ParseExperimentView: ['parse_experiment', 'parse_experiment_bio_feature_reporter',
                              'parse_experiment_raw_data', 'parse_experiment_platform'],
        ScriptTreeView: ['script_tree'],
        FileAssignmentView: ['file_assignment_list', 'file_assignment', 'experiment_file_assignment',
                             'platform_file_assignment', 'sample_file_assignment'],
        MessageLogView: ['message_log'],
        ExportDataView: ['export_data'],
        TestView: ['test'],
        OntologiesView: ['ontologies', 'view_ontology', 'window_new_ontology', 'window_new_ontology_node'],
        JupyterNotebookView: ['jupyter_notebook', 'notebook_tree'],
        NormalizationManagerView: ['normalization_manager', 'normalization', 'window_new_normalization',
                                   'window_add_experiment', 'win_normalization_manager'],
        NormalizationExperimentView: ['normalization_experiment']
    }

    @staticmethod
    def get_view(view_name):
        for cl, views in Dispatcher.dispatcher.items():
            if view_name in views:
                return cl()
        raise NotImplementedError("View {} doesn't have consumer class".format(view_name))


class GroupCompendiumPermission:

    _view_permission = collections.OrderedDict({
        CommandPermission.PARSE_EXPERIMENT: [ParseExperimentView],
        CommandPermission.DOWNLOAD_UPLOAD_EXPERIMENT: [ExperimentPublicView],
        CommandPermission.REPORTER_MAPPING: [MicroarrayPlatformView],
        CommandPermission.ADD_BIOFEATURE: [BioFeatureGeneView]
    })

    _default_view = [
        ExperimentView,
        MessageLogView,
        PlatformView,
        BioFeatureView
    ]

    @staticmethod
    def get_permitted_views(user):
        permitted_db = GroupCompendiumPermission.get_permitted_db(user)
        views = {db: [] for db in permitted_db}
        views['no_compendium'] = []
        all_views = [v for i in Dispatcher.dispatcher.values() for v in i]
        default = [v for i in GroupCompendiumPermission._default_view for v in Dispatcher.dispatcher[i]]
        for db in CompendiumDatabase.objects.all():
            if user.is_staff and user.is_superuser:
                views[db.compendium_nick_name] = list(all_views)
                views['no_compendium'] = list(all_views)
            elif db.compendium_nick_name in permitted_db:
                views[db.compendium_nick_name].extend(default)
                views['no_compendium'].extend(default)
        for g in user.groups.all():
            for p in g.permissions.all():
                if p.codename in GroupCompendiumPermission._view_permission:
                    for view_class in GroupCompendiumPermission._view_permission[p.codename]:
                        views[p.content_type.app_label].extend(
                            Dispatcher.dispatcher[view_class]
                        )
        return views

    @staticmethod
    def get_permitted_db(user):
        return set([p.content_type.app_label for g in user.groups.all() for p in g.permissions.all()])

    @staticmethod
    def get_permission(permission_type, compendium_db):
        p = None
        ct = None
        try:
            ct = ContentType.objects.get(app_label=compendium_db.compendium_nick_name)
        except Exception as e:
            ct = ContentType()
            ct.app_label = compendium_db.compendium_nick_name
            ct.save()
        try:
            p = Permission.objects.get(content_type=ct, codename=permission_type)
        except Exception as e:
            p = Permission()
            p.content_type = ct
            p.codename = permission_type
            p.name = CommandPermission.names[permission_type]
            p.save()
        return p

    @staticmethod
    def get_all_permissions():
        return [{'codename': k, 'name': v, 'selected': False} for k, v in CommandPermission.names.items()]


@channel_session_user_from_http
def ws_connect(message):
    if message.user.is_active and message.user.is_staff and message.user.is_superuser:
        Group("admin").add(message.reply_channel)
    for db in CompendiumDatabase.objects.all():
        Group("compendium_" + str(db.id)).add(message.reply_channel)
    message.http_session['channel_name'] = message.reply_channel.name
    message.reply_channel.send({"accept": True})


@channel_session_user
def ws_receive(message):
    channel_request = json.loads(message.content['text'])
    channel_name = message.content['reply_channel']
    view = channel_request['stream']
    request = channel_request['payload']
    operation = request['operation']
    user_id = message.user.id

    cls = Dispatcher.get_view(view)
    method = getattr(cls, operation)
    method(channel_name, view, request, message.user)


@channel_session_user
def ws_disconnect(message):
    Group("admin").discard(message.reply_channel)
    for db in CompendiumDatabase.objects.all():
        Group("compendium_" + str(db.id)).discard(message.reply_channel)
    print('close connection!')
    message.reply_channel.send({"accept": False, "close": True})

"""compass_v2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from command import views
from command.lib.views.admin_options_view import AdminOptionsView
from command.lib.views.bio_feature import BioFeatureView, BioFeatureGeneView
from command.lib.views.bio_feature_anno import BioFeatureAnnoView
from command.lib.views.bio_feature_reporter import BioFeatureReporterView
from command.lib.views.compendium_manager import CompendiumManagerView
from command.lib.views.experiment_local import ExperimentLocalView
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

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^check_login/$', views.check_login, name='check_login'),
    url(r'^reset_password/$', views.reset_password, name='reset_password'),
    url(r'^do_logout/$', views.do_logout, name='do_logout'),
    url(r'^update_permission/$', views.update_permission, name='update_permission'),
    url(r'^admin_options/(?P<operation>\w+)$', AdminOptionsView.as_view(), name='admin_options'),
    url(r'^users/(?P<operation>\w+)$', UserGroupManagerView.as_view(), name='users'),
    url(r'^groups/(?P<operation>\w+)$', UserGroupManagerView.as_view(), name='groups'),
    url(r'^privileges/(?P<operation>\w+)$', CompendiumManagerView.as_view(), name='privileges'),
    url(r'^compendia/(?P<operation>\w+)$', CompendiumManagerView.as_view(), name='compendia'),
    url(r'^compendium_types/(?P<operation>\w+)$', CompendiumManagerView.as_view(), name='compendium_types'),
    url(r'^experiment_public/(?P<operation>\w+)$', ExperimentPublicView.as_view(), name='experiment_public'),
    url(r'^experiment_local/(?P<operation>\w+)$', ExperimentLocalView.as_view(), name='experiment_local'),
    url(r'^experiments/(?P<operation>\w+)$', ExperimentView.as_view(), name='experiments'),
    url(r'^platforms/(?P<operation>\w+)$', PlatformView.as_view(), name='platforms'),
    url(r'^parse_experiment/(?P<operation>\w+)/(?P<exp_id>\d+)$', ParseExperimentView.as_view(), name='parse_experiment'),
    url(r'^script_tree/(?P<operation>\w+)$', ScriptTreeView.as_view(), name='script_tree'),
    url(r'^file_assignment/(?P<operation>\w+)$', FileAssignmentView.as_view(), name='file_assignment'),
    url(r'^file_assignment_list/(?P<operation>\w+)$', FileAssignmentView.as_view(), name='file_assignment'),
    url(r'^experiment_file_assignment/(?P<operation>\w+)$', FileAssignmentView.as_view(), name='file_assignment'),
    url(r'^platform_file_assignment/(?P<operation>\w+)$', FileAssignmentView.as_view(), name='platform_file_assignment'),
    url(r'^sample_file_assignment/(?P<operation>\w+)$', FileAssignmentView.as_view(), name='sample_file_assignment'),
    url(r'^message_log/(?P<operation>\w+)$', MessageLogView.as_view(), name='message_log'),
    url(r'^bio_feature/(?P<operation>\w+)$', BioFeatureView.as_view(), name='bio_feature'),
    url(r'^bio_feature_gene/(?P<operation>\w+)$', BioFeatureGeneView.as_view(), name='bio_feature_gene'),
    url(r'^bio_feature_reporter/(?P<operation>\w+)$', BioFeatureReporterView.as_view(), name='bio_feature_reporter'),
    url(r'^export_data/(?P<operation>\w+)$', ExportDataView.as_view(), name='export_data'),
    url(r'^microarray_platforms/(?P<operation>\w+)$', MicroarrayPlatformView.as_view(), name='microarray_platforms'),
    url(r'^check_bio_features/$', views.check_bio_features, name='check_bio_features'),
    url(r'^ontologies/(?P<operation>\w+)$', OntologiesView.as_view(), name='ontologies'),
    url(r'^bio_feature_anno/(?P<operation>\w+)$', BioFeatureAnnoView.as_view(), name='bio_feature_anno'),
    url(r'^jupyter_notebook/(?P<operation>\w+)$', JupyterNotebookView.as_view(), name='jupyter_notebook'),
    url(r'^normalization_manager/(?P<operation>\w+)$', NormalizationManagerView.as_view(), name='normalization_manager'),
    url(r'^normalization_experiment/(?P<operation>\w+)$', NormalizationExperimentView.as_view(), name='normalization_experiment'),

    url(r'^test/(?P<operation>\w+)$', TestView.as_view(), name='test'),
]

import importlib
import os
from contextlib import closing

import django.apps
import shutil
from django.core.management import call_command
from django.db import connections, transaction

from command.lib.db.compendium.annotation_value import AnnotationValue
from command.lib.db.compendium.bio_feature_annotation import BioFeatureAnnotation
from command.lib.db.compendium.normalization import Normalization
from command.lib.db.compendium.normalization_experiment import NormalizationExperiment
from command.lib.db.compendium.normalization_design_group import NormalizationDesignGroup
from command.lib.db.compendium.normalization_design_sample import NormalizationDesignSample
from command.lib.db.compendium.normalized_data import NormalizedData
from command.lib.db.compendium.ontology import Ontology
from command.lib.db.compendium.ontology_edge import OntologyEdge
from command.lib.db.compendium.ontology_node import OntologyNode
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.bio_feature_fields_admin import BioFeatureFieldsAdmin
from command.lib.db.admin.bio_feature_reporter_fields_admin import BioFeatureReporterFieldsAdmin
from command.lib.db.admin.platform_type_admin import PlatformTypeAdmin
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.bio_feature_reporter_values import BioFeatureReporterValues
from command.lib.db.compendium.bio_feature_values import BioFeatureValues
from command.lib.db.compendium.raw_data import RawData
from command.lib.db.compendium.platform_type import PlatformType
from command.lib.db.compendium.bio_feature_reporter_fields import BioFeatureReporterFields
from command.lib.db.compendium.bio_feature_fields import BioFeatureFields
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.sample_annotation import SampleAnnotation
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.value_type import ValueType
from command.lib.db.parsing.parsing_bio_feature_reporter import ParsingBioFeatureReporter
from command.lib.db.parsing.parsing_experiment import ParsingExperiment
from command.lib.db.parsing.parsing_platform import ParsingPlatform
from command.lib.db.parsing.parsing_sample import ParsingSample
from command.lib.utils.queryset_iterator import queryset_to_csv, batch_qs
from command.models import init_database_connections
from cport import settings


def init_parsing(db_id, exp_id, get_name_only=False):
    init_database_connections()
    compendium = CompendiumDatabase.objects.get(id=db_id)
    experiment = Experiment.objects.using(compendium.compendium_nick_name).get(id=exp_id)
    base_dir = AdminOptions.objects.get(option_name='raw_data_directory')
    out_dir = os.path.join(base_dir.option_value, compendium.compendium_nick_name,
                           experiment.experiment_access_id)
    os.makedirs(out_dir, exist_ok=True)
    key = os.path.join(out_dir, experiment.experiment_access_id + '.sqlite')
    if get_name_only:
        return key
    value = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': key,
        'PARSING': True
    }
    connections.databases[key] = value
    try:
        exp = ParsingExperiment.objects.using(key).all()[0]
    except Exception as e:
        call_command('migrate', database=key)
        module_name, class_name = '.'.join(experiment.data_source.python_class.split('.')[:-1]), \
                                  experiment.data_source.python_class.split('.')[-1]
        python_class = getattr(importlib.import_module(module_name), class_name)()
        exp = ParsingExperiment()
        exp.organism = experiment.organism
        exp.experiment_access_id = experiment.experiment_access_id
        exp.description = experiment.description
        exp.experiment_name = experiment.experiment_name
        if experiment.scientific_paper_ref:
            exp.scientific_paper_ref = python_class.scientific_paper_accession_base_link + experiment.scientific_paper_ref
        exp.experiment_fk = experiment.id
        exp.save(using=key)
    try:
        ParsingPlatform.objects.using(key).all()[0]
    except Exception as e:
        platform_ids = list(set([sample.platform_id for sample in experiment.sample_set.all() if sample.platform_id]))
        for platform_id in platform_ids:
            platform = Platform.objects.using(compendium.compendium_nick_name).get(id=platform_id)
            plt = ParsingPlatform()
            plt.platform_access_id = platform.platform_access_id
            plt.platform_name = platform.platform_name
            plt.description = platform.description
            plt.platform_type = platform.platform_type.name if platform.platform_type else None
            plt.platform_fk = platform_id
            plt.reporter_platform = platform_id
            plt.reporter_platform_imported = platform.biofeaturereporter_set.count() > 0
            plt.save(using=key)
    try:
        ParsingSample.objects.using(key).all()[0]
    except Exception as e:
        for sample in experiment.sample_set.all():
            plt = ParsingPlatform.objects.using(key).get(platform_fk=sample.platform_id)
            smp = ParsingSample()
            smp.sample_name = sample.sample_name
            smp.description = sample.description
            smp.experiment = exp
            smp.platform = plt
            smp.sample_fk = sample.id
            smp.reporter_platform = plt.reporter_platform
            smp.reporter_platform_imported = plt.reporter_platform_imported
            smp.save(using=key)

    return key


def init_compendium(db_id):
    compendium = CompendiumDatabase.objects.get(id=db_id)
    key = compendium.compendium_nick_name
    value = {}
    if compendium.db_engine == 'SQLite':
        value = {
            'NAME': key,
            'ENGINE': 'django.db.backends.sqlite3'
        }
    elif compendium.db_engine == 'django.db.backends.postgresql' or compendium.db_engine == 'django.db.backends.postgresql_psycopg2':
        value = {
            'ENGINE': compendium.db_engine,
            'NAME': key,
            'USER': compendium.db_user,
            'PASSWORD': compendium.db_password,
            'PORT': compendium.db_port,
            'HOST': compendium.db_host
        }
    connections.databases[key] = value
    cursor = connections[key].cursor()
    models = [m for m in django.apps.apps.get_models()]
    for model in models:
        if 'command.lib.db.compendium' in model.__module__:
            table = model._meta.db_table
            try:
                cursor.execute("TRUNCATE TABLE " + table + " CASCADE")
            except Exception as e:
                pass
    call_command('migrate', database=key)
    if compendium.compendium_type.name == 'gene_expression':
        ValueType(name='I', description='Intensity').save(using=key)
        ValueType(name='BG', description='BackGround').save(using=key)
        ValueType(name='IBG', description='Intensity Background corrected').save(using=key)
        ValueType(name='M', description='M-value, Intensity log-ratio').save(using=key)
        ValueType(name='A', description='A-value, Intensity average').save(using=key)
        ValueType(name='C', description='Count').save(using=key)
        geo_db = DataSource(source_name='GEO',
                            python_class='command.lib.coll.public_database.GEOPublicDatabase',
                            is_local=False)
        geo_db.save(using=key)
        ae_db = DataSource(source_name='ArrayExpress',
                            python_class='command.lib.coll.public_database.ArrayExpressPublicDatabase',
                            is_local=False)
        ae_db.save(using=key)
        sra_db = DataSource(source_name='SRA',
                           python_class='command.lib.coll.public_database.SRAPublicDatabase',
                           is_local=False)
        sra_db.save(using=key)
    local_data = DataSource(source_name='local',
                        python_class='command.lib.coll.local_data_source.LocalDataSource',
                        is_local=True)
    local_data.save(using=key)
    status_new = Status(name='experiment_new', description='Experiment never seen before')
    status_scheduled = Status(name='experiment_scheduled', description='Experiment scheduled for later processing')
    status_downloading = Status(name='experiment_downloading', description='Experiment is downloading')
    status_data_ready = Status(name='experiment_data_ready', description='All experiment data are downloaded')
    status_raw_data_importing = Status(name='experiment_raw_data_importing', description='Experiment raw data is being imported')
    status_raw_data_imported = Status(name='experiment_raw_data_imported', description='Experiment raw data are imported')
    status_exluded = Status(name='experiment_excluded',
                                      description='Experiment not suitable for this compendium')
    status_new.save(using=key)
    status_scheduled.save(using=key)
    status_downloading.save(using=key)
    status_data_ready.save(using=key)
    status_raw_data_imported.save(using=key)
    status_raw_data_importing.save(using=key)
    status_exluded.save(using=key)
    status_ready = Status(name='entity_script_ready', description='Entity is ready to be parsed')
    status_running = Status(name='entity_script_running', description='Entity is being parsed')
    status_error = Status(name='entity_script_error', description='Entity parsing reported an error')
    status_parsed = Status(name='entity_script_parsed', description='Entity is parsed')
    status_scheduled = Status(name='entity_script_scheduled', description='Entity is scheduled to be parsed')
    status_ready.save(using=key)
    status_running.save(using=key)
    status_error.save(using=key)
    status_parsed.save(using=key)
    status_scheduled.save(using=key)
    status_platform_importing = Status(name='platform_importing', description='Platform is being imported')
    status_platform_imported = Status(name='platform_imported', description='Platform is imported')
    status_platform_importing.save(using=key)
    status_platform_imported.save(using=key)
    status_annotated = Status(name='experiment_annotated', description='Experiment samples have been annotated')
    status_design_defined = Status(name='experiment_design_defined', description='Experiment design has been defined')
    status_normalized = Status(name='experiment_normalized', description='Experiment has been normalized')
    status_annotated.save(using=key)
    status_design_defined.save(using=key)
    status_normalized.save(using=key)
    # copy over data from platform type and biological features tables
    for plt_type_admin in PlatformTypeAdmin.objects.all():
        plt_type = PlatformType()
        plt_type.id = plt_type_admin.id
        plt_type.name = plt_type_admin.name
        plt_type.description = plt_type_admin.description
        plt_type.bio_feature_reporter_name = plt_type_admin.bio_feature_reporter_name
        plt_type.save(using=key)
    for bio_ff_admin in BioFeatureFieldsAdmin.objects.all():
        bio_ff = BioFeatureFields()
        bio_ff.id = bio_ff_admin.id
        bio_ff.name = bio_ff_admin.name
        bio_ff.description = bio_ff_admin.description
        bio_ff.feature_type = bio_ff_admin.feature_type
        bio_ff.save(using=key)
    for bio_frf_admin in BioFeatureReporterFieldsAdmin.objects.all():
        bio_frf = BioFeatureReporterFields()
        bio_frf.id = bio_frf_admin.id
        bio_frf.name = bio_frf_admin.name
        bio_frf.description = bio_frf_admin.description
        bio_frf.platform_type = PlatformType.objects.using(key).get(id=bio_frf_admin.platform_type_id)
        bio_frf.feature_type = bio_frf_admin.feature_type
        bio_frf.save(using=key)
    # remove data
    base_dir = AdminOptions.objects.get(option_name='download_directory').option_value
    full_dir = os.path.join(base_dir, compendium.compendium_nick_name)
    if os.path.exists(full_dir) and os.path.isdir(full_dir):
        shutil.rmtree(full_dir)
    base_dir = AdminOptions.objects.get(option_name='raw_data_directory').option_value
    full_dir = os.path.join(base_dir, compendium.compendium_nick_name)
    if os.path.exists(full_dir) and os.path.isdir(full_dir):
        shutil.rmtree(full_dir)

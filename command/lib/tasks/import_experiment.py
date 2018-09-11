from __future__ import absolute_import, unicode_literals

import csv
import glob
import importlib
import json
import os
from contextlib import closing

import celery
import math
from celery.contrib.abortable import AbortableTask
from channels import Group, Channel
from django.contrib.auth.models import User
from django.db import connections, transaction, IntegrityError, DatabaseError

from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.bio_feature_reporter_fields import BioFeatureReporterFields
from command.lib.db.compendium.bio_feature_reporter_values import BioFeatureReporterValues
from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.experiment_search_result import ExperimentSearchResult
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.platform_type import PlatformType
from command.lib.db.compendium.raw_data import RawData
from command.lib.db.compendium.sample import Sample
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.view_task import ViewTask
from command.lib.db.parsing.parsing_bio_feature_reporter_values import ParsingBioFeatureReporterValues
from command.lib.db.parsing.parsing_experiment import ParsingExperiment
from command.lib.db.parsing.parsing_platform import ParsingPlatform
from command.lib.db.parsing.parsing_sample import ParsingSample
from command.lib.utils.init_compendium import init_parsing
from command.lib.utils.message import Message
from command.lib.utils.queryset_iterator import queryset_iterator, batch_qs
from command.models import init_database_connections
from cport import settings


class ImportExperimentPlatformCallbackTask(AbortableTask, celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, experiment_id, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
        parsing_db = init_parsing(compendium_id, experiment_id)
        platforms = [plt.platform_access_id for plt in ParsingPlatform.objects.using(parsing_db).all()]
        log = MessageLog()
        log.title = "Platforms: " + ", ".join(platforms) + " imported"
        log.message = "Status: success, Platforms: " + ", ".join(platforms) + ", Experiment: " + \
                      exp.experiment_access_id + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username + \
                      " Results: " + retval
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)
        # delete CSV file
        for fl in glob.glob(parsing_db + '*bio_feature*.csv'):
            os.remove(fl)
        message = Message(type='info', title='Successfully imported platforms',
                          message='Successfully imported platforms for experiment ' + exp.experiment_access_id +
                          ' (' + ','.join(platforms) + ') <br>' + retval
                          )
        message.send_to(channel)
        ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='platform_imported')
        for parsing_platform in ParsingPlatform.objects.using(parsing_db).all():
            plt = Platform.objects.using(compendium.compendium_nick_name).get(id=parsing_platform.platform_fk)
            plt.status = ready_status
            plt.save(using=compendium.compendium_nick_name)
        Group("compendium_" + str(compendium_id) + "_" + str(experiment_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, experiment_id, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
        parsing_db = init_parsing(compendium_id, experiment_id)
        platforms = [plt.platform_access_id for plt in ParsingPlatform.objects.using(parsing_db).all()]
        log = MessageLog()
        log.title = "Platforms: " + ", ".join(platforms) + " error"
        log.message = "Status: error, Platforms: " + ", ".join(platforms) + ", Experiment: " + \
                      exp.experiment_access_id + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                      ", Exception: " \
                      + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)
        # delete CSV file
        for fl in glob.glob(parsing_db + '*bio_feature*.csv'):
            os.remove(fl)
        message = Message(type='error', title='Error on importing platforms for experiment ' + exp.experiment_access_id, message=str(exc))
        message.send_to(channel)
        for parsing_platform in ParsingPlatform.objects.using(parsing_db).all():
            plt = Platform.objects.using(compendium.compendium_nick_name).get(id=parsing_platform.platform_fk)
            plt.status = None
            plt.save(using=compendium.compendium_nick_name)
        Group("compendium_" + str(compendium_id) + "_" + str(experiment_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })


class ImportExperimentCallbackTask(AbortableTask, celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, experiment_id, keep_platform, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
        parsing_db = init_parsing(compendium_id, experiment_id)
        report = retval
        log = MessageLog()
        log.title = "Experiment: " + exp.experiment_access_id + " imported"
        log.message = "Status: success, Experiment: " + exp.experiment_access_id + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username + \
            " Results: " + report
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        # delete CSV files
        try:
            for fl in glob.glob(parsing_db + '*.csv'):
                os.remove(fl)
        except Exception as e:
            pass
        message = Message(type='info', title='Successfully imported experiment',
                          message='Successfully imported experiment ' + exp.experiment_access_id +
                                  '<br>' + report
                          )
        message.send_to(channel)
        imported_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_raw_data_imported')
        exp.status = imported_status
        exp.save(using=compendium.compendium_nick_name)
        Group("compendium_" + str(compendium_id) + "_" + str(experiment_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, experiment_id, keep_platform, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
        parsing_db = init_parsing(compendium_id, experiment_id)
        log = MessageLog()
        log.title = "Experiment: " + exp.experiment_access_id + " imported"
        log.message = "Status: error, Experiment: " + exp.experiment_access_id + ", Task: " + task_id + ", User: " +\
                      User.objects.get(id=user_id).username + ", Exception: " \
                      + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)
        # delete CSV file
        for fl in glob.glob(parsing_db + '*.csv'):
            os.remove(fl)
        message = Message(type='error', title='Error on importing experiment ' + exp.experiment_access_id, message=str(exc))
        message.send_to(channel)
        data_ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_data_ready')
        exp.status = data_ready_status
        exp.save(using=compendium.compendium_nick_name)
        Group("compendium_" + str(compendium_id) + "_" + str(experiment_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })


def __import_rnaseq_platform(compendium, platform):
    platform.biofeaturereporter_set.all().delete()
    rna_seq_reporters = []
    for gid, gname in BioFeature.objects.using(compendium.compendium_nick_name).values_list('id', 'name'):
        rep = BioFeatureReporter()
        rep.name = gname
        rep.description = gname
        rep.platform_id = platform.id
        rep.bio_feature_id = gid
        rna_seq_reporters.append(rep)
    BioFeatureReporter.objects.using(compendium.compendium_nick_name).bulk_create(rna_seq_reporters)


def __import_experiment_platform(compendium, parsing_db, reporters_batch_size):
    report = ''
    imported_platforms = []
    with transaction.atomic(using=compendium.compendium_nick_name):
        for parsing_platform in ParsingPlatform.objects.using(parsing_db).all():
            reporter_count = 0
            plt = Platform.objects.using(compendium.compendium_nick_name).get(id=parsing_platform.platform_fk)
            if parsing_platform.platform_type == 'rnaseq':
                __import_rnaseq_platform(compendium, plt)
            else:
                plt.biofeaturereporter_set.all().delete()
                imported_platforms.append(plt.id)
                plt.platform_access_id = parsing_platform.platform_access_id
                plt.platform_name = parsing_platform.platform_name
                plt.description = parsing_platform.description
                try:
                    plt.platform_type = PlatformType.objects.using(compendium.compendium_nick_name). \
                        get(name=parsing_platform.platform_type)
                except Exception as dbe:
                    raise DatabaseError('You need to specify a valid platform type')
                plt.save(using=compendium.compendium_nick_name)
                # feature reporter
                bio_feature_reporter_csv = os.path.join(
                    os.path.dirname(parsing_db),
                    os.path.basename(parsing_db) + '_bio_feature_reporter.csv')
                reporter_count += parsing_platform.parsingbiofeaturereporter_set.count()
                with open(bio_feature_reporter_csv, 'w') as csvfile_rep:
                    writer_rep = csv.writer(csvfile_rep, delimiter='\t')
                    for reporter in parsing_platform.parsingbiofeaturereporter_set.all():
                        writer_rep.writerow([reporter.name, reporter.description, plt.id])
                csvfile_rep = open(bio_feature_reporter_csv)
                with closing(connections[compendium.compendium_nick_name].cursor()) as cursor:
                    cursor.copy_from(
                        file=csvfile_rep,
                        table=BioFeatureReporter._meta.db_table,
                        sep='\t',
                        columns=('name', 'description', 'platform_id')
                    )
                csvfile_rep.close()
    with transaction.atomic(using=compendium.compendium_nick_name):
        for parsing_platform in ParsingPlatform.objects.using(parsing_db).all():
            plt = Platform.objects.using(compendium.compendium_nick_name).get(id=parsing_platform.platform_fk)
            if parsing_platform.platform_type == 'rnaseq':
                continue
            if plt.id not in imported_platforms:
                continue
            bio_feature_reporter_fields = {field.name: field.id for field in
                                           BioFeatureReporterFields.objects.using(
                                               compendium.compendium_nick_name).
                                               filter(platform_type=plt.platform_type)
            }
            bio_feature_reporter_values_csv = os.path.join(
                os.path.dirname(parsing_db),
                os.path.basename(parsing_db) + '_bio_feature_reporter_values.csv')
            reporter_count = 0
            for start, end, total, qs in batch_qs(plt.biofeaturereporter_set.get_queryset().order_by('id'), batch_size=reporters_batch_size):
                parsing_reporters = parsing_platform.parsingbiofeaturereporter_set.filter(name__in=[r.name for r in qs])
                reporter_count += parsing_reporters.count()
                with open(bio_feature_reporter_values_csv, 'w') as csvfile_val:
                    writer_val = csv.writer(csvfile_val, delimiter='\t')
                    for pr, r in zip(parsing_reporters, qs.all()):
                        for value in pr.parsingbiofeaturereportervalues_set.all():
                            field_id = bio_feature_reporter_fields[value.bio_feature_reporter_field]
                            writer_val.writerow([r.id, field_id, value.value])

                csvfile_val = open(bio_feature_reporter_values_csv)
                with closing(connections[compendium.compendium_nick_name].cursor()) as cursor:
                    cursor.copy_from(
                        file=csvfile_val,
                        table=BioFeatureReporterValues._meta.db_table,
                        sep='\t',
                        columns=('bio_feature_reporter_id', 'bio_feature_reporter_field_id', 'value')
                    )
                csvfile_val.close()
            report += 'Platform: ' + plt.platform_access_id + ' ' + str(reporter_count) + ' imported<br>'
    return report


@celery.task(base=ImportExperimentCallbackTask, bind=True)
def import_experiment(self, user_id, compendium_id, experiment_id, keep_platform, channel_name, view, operation):
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    parsing_db = init_parsing(compendium_id, experiment_id)
    reporters_batch_size = 1000
    raw_data_batch_size = 1000

    data_importing_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_raw_data_importing')

    with transaction.atomic(using=compendium.compendium_nick_name):
        exp = Experiment.objects.using(compendium.compendium_nick_name).get(id=experiment_id)
        parsing_exp = ParsingExperiment.objects.using(parsing_db).all()[0]
        exp.experiment_access_id = parsing_exp.experiment_access_id
        exp.organism = parsing_exp.organism
        exp.experiment_name = parsing_exp.experiment_name
        exp.scientific_paper_ref = parsing_exp.scientific_paper_ref
        exp.description = parsing_exp.description
        exp.status = data_importing_status
        exp.save(using=compendium.compendium_nick_name)

    Group("compendium_" + str(compendium.id) + "_" + str(experiment_id)).send({
        'text': json.dumps({
            'stream': view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })

    report = ''
    if not keep_platform:
        report = __import_experiment_platform(compendium, parsing_db, reporters_batch_size)

    with transaction.atomic(using=compendium.compendium_nick_name):
        for parsing_sample in ParsingSample.objects.using(parsing_db).all():
            smp = Sample.objects.using(compendium.compendium_nick_name).get(id=parsing_sample.sample_fk)
            smp.sample_name = parsing_sample.sample_name
            smp.description = parsing_sample.description
            smp.reporter_platform_id = parsing_sample.reporter_platform
            smp.save(using=compendium.compendium_nick_name)
            if parsing_sample.parsingrawdata_set.count():
                smp.rawdata_set.all().delete()
            raw_data_csv = os.path.join(
                os.path.dirname(parsing_db),
                os.path.basename(parsing_db) + '_raw_data.csv')
            reporter_counter = 0
            for start, end, total, qs in batch_qs(parsing_sample.parsingrawdata_set.get_queryset().order_by('id'),
                                                  batch_size=raw_data_batch_size):
                reporters = {x['name']: x['id'] for x in
                    smp.reporter_platform.biofeaturereporter_set.filter(name__in=[r.bio_feature_reporter_name for r in qs]).values('id', 'name')}
                reporter_counter += len(reporters)
                with open(raw_data_csv, 'w') as csvfile_val:
                    writer_val = csv.writer(csvfile_val, delimiter='\t')
                    for raw_data in qs.all():
                        if raw_data.bio_feature_reporter_name in reporters:
                            writer_val.writerow([smp.id, reporters[raw_data.bio_feature_reporter_name], raw_data.value])

                csvfile_val = open(raw_data_csv)
                with closing(connections[compendium.compendium_nick_name].cursor()) as cursor:
                    cursor.copy_from(
                        file=csvfile_val,
                        table=RawData._meta.db_table,
                        sep='\t',
                        columns=('sample_id', 'bio_feature_reporter_id', 'value')
                    )
                csvfile_val.close()
            report += 'Sample: ' + smp.sample_name + ' ' + str(reporter_counter) + ' imported<br>'
    return report


@celery.task(base=ImportExperimentPlatformCallbackTask, bind=True)
def import_experiment_platform(self, user_id, compendium_id, experiment_id, channel_name, view, operation):
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    parsing_db = init_parsing(compendium_id, experiment_id)
    reporters_batch_size = 1000
    importing_status = Status.objects.using(compendium.compendium_nick_name).get(name='platform_importing')
    for parsing_platform in ParsingPlatform.objects.using(parsing_db).all():
        plt = Platform.objects.using(compendium.compendium_nick_name).get(id=parsing_platform.platform_fk)
        plt.status = importing_status
        plt.save(using=compendium.compendium_nick_name)
    Group("compendium_" + str(compendium.id) + "_" + str(experiment_id)).send({
        'text': json.dumps({
            'stream': view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })
    return __import_experiment_platform(compendium, parsing_db, reporters_batch_size)


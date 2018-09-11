import csv
import glob
import json
import os
import subprocess
from contextlib import closing

import celery
import math
from Bio.Blast.Applications import NcbiblastnCommandline
from celery.contrib.abortable import AbortableTask
from channels import Group, Channel
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connections, transaction, DatabaseError

from command.lib.coll.platform.microarray_mapper import MicroarrayMapper
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.view_task import ViewTask
from command.lib.utils.message import Message
from command.lib.utils.queryset_iterator import chunks
from command.models import init_database_connections


class ImportPlatformMappingCallbackTask(AbortableTask, celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, plt_dir, platform_id, filter_id, \
            blast_file_name, channel_name, view, operation = args
        csv_file, without_mapping_before, with_mapping_before = retval
        without_mapping_before = set(without_mapping_before)
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        without_mapping_after = set(BioFeatureReporter.objects.using(compendium.compendium_nick_name).filter(
            platform_id=platform_id, bio_feature__isnull=True
        ).values_list('id', flat=True).distinct())
        with_mapping_after = dict(BioFeatureReporter.objects.using(compendium.compendium_nick_name).filter(
            platform_id=platform_id, bio_feature__isnull=False
        ).values_list('id', 'bio_feature_id'))
        added = len(set.intersection(without_mapping_before, set(with_mapping_after.keys())))
        removed = len(set.intersection(set(with_mapping_before.keys()), without_mapping_after))
        changed = len(set.intersection(set(with_mapping_before.keys()), set(with_mapping_after.keys()))) - \
                  len(set.intersection(set(with_mapping_before.items()), set(with_mapping_after.items())))
        unchanged_mapped = len(set.intersection(set(with_mapping_before.items()), set(with_mapping_after.items())))
        unchanged_unmapped = len(
            set.intersection(without_mapping_before, without_mapping_after))
        report = 'added: {}, removed: {}, changed: {}, unchanged_mapped: {}, unchanged_unmapped: {}'.format(
            added, removed, changed, unchanged_mapped, unchanged_unmapped
        )
        plt = Platform.objects.using(compendium.compendium_nick_name).get(id=platform_id)
        log = MessageLog()
        log.title = "Platform: " + plt.platform_access_id + " mapping imported"
        log.message = "Status: success, Platform: " + plt.platform_access_id +\
                      ", Report: " + report + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)
        # delete CSV file
        try:
            os.remove(csv_file)
        except Exception as e:
            pass
        message = Message(type='info', title='Successfully imported platform mapping',
                          message='Successfully imported mapping for platform ' + plt.platform_access_id + '. ' + report
                          )
        message.send_to(channel)
        for blast_file in glob.glob(plt_dir + "/*.blast"):
            mapper = MicroarrayMapper(os.path.join(plt_dir, blast_file))
            mapper.set_imported(False)
        mapper = MicroarrayMapper(os.path.join(plt_dir, blast_file_name))
        mapper.set_imported(True, filter_id)
        mapper.set_filter_status(filter_id, 'ready')
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, plt_dir, platform_id, filter_id, \
        blast_file_name, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)

        log = MessageLog()
        plt = Platform.objects.using(compendium.compendium_nick_name).get(id=platform_id)
        log.title = "Platform: " + plt.platform_access_id + " importing mapping error"
        log.message = "Status: error, Platform: " + plt.platform_access_id + \
                      ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                      ", Exception: " + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        message = Message(type='error', title='Error during importing platform mapping',
                          message=str(exc)
                          )
        message.send_to(channel)
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })


@celery.task(base=ImportPlatformMappingCallbackTask, bind=True)
def import_platform_mapping(self, user_id, compendium_id, plt_dir, platform_id,
                            filter_id, blast_file_name, channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    try:
        ViewTask.objects.using(compendium.compendium_nick_name). \
            get(view=view, operation=operation).delete()
    except Exception as e:
        pass
    channel_task = ViewTask(task_id=task_id, operation=operation, view=view)
    channel_task.save(using=compendium.compendium_nick_name)

    mapper = MicroarrayMapper(os.path.join(plt_dir, blast_file_name))
    mapper.set_filter_status(filter_id, 'running')
    Group("compendium_" + str(compendium_id)).send({
        'text': json.dumps({
            'stream': view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })
    chunk_size = 30000
    start = 0
    total = mapper.get_filter_result_count()
    bio_feature_reporter_mapping_csv = os.path.join(
        plt_dir, blast_file_name) + '_bio_feature_reporter_mapping.csv'
    try:
        os.remove(bio_feature_reporter_mapping_csv)
    except Exception as e:
        pass
    with transaction.atomic(using=compendium.compendium_nick_name):
        without_mapping_before = set(BioFeatureReporter.objects.using(compendium.compendium_nick_name).filter(
            platform_id=platform_id, bio_feature__isnull=True
        ).values_list('id', flat=True).distinct())
        with_mapping_before = dict(BioFeatureReporter.objects.using(compendium.compendium_nick_name).filter(
            platform_id=platform_id, bio_feature__isnull=False
        ).values_list('id', 'bio_feature_id'))
        BioFeatureReporter.objects.using(compendium.compendium_nick_name).\
            filter(platform_id=platform_id).update(bio_feature=None)
        for chunk_num in range(int(math.ceil(total / chunk_size))):
            chunk = mapper.get_filter_result_dict(filter_id, start, start + chunk_size, self.is_aborted)
            if self.is_aborted():
                raise DatabaseError('Operation aborted by user')
            for rep_id, feat_id in chunk.items():
                BioFeatureReporter.objects.using(compendium.compendium_nick_name).\
                    filter(id=rep_id).update(bio_feature_id=feat_id)
            start += chunk_size

    return bio_feature_reporter_mapping_csv, list(without_mapping_before), with_mapping_before

import glob
import json
import os

import celery
from channels import Group, Channel
from django.contrib.auth.models import User
from django.db import connections

from command.lib.coll.biological_feature import importers
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.platform_type import PlatformType
from command.lib.db.compendium.raw_data import RawData
from command.lib.db.compendium.sample import Sample
from command.lib.utils.file_system import compress_gz
from command.lib.utils.message import Message
from command.lib.utils.queryset_iterator import batch_qs
from command.models import init_database_connections
import time
import pandas as pd
import numpy as np


class ExportRawDataCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, path, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        filename_tsv = os.path.basename(str(retval))
        filename_hdf5 = os.path.basename(str(retval).replace('.tsv.gz', '.hdf5'))
        url_tsv = '/export_data/read_file?path=' + str(retval)
        url_hdf5 = '/export_data/read_file?path=' + str(retval).replace('.tsv.gz', '.hdf5')
        log = MessageLog()
        log.title = "Export raw data"
        log.message = "Status: success, <br> File TSV:  <a href='" + url_tsv + "'>" + filename_tsv + "</a>, <br>" \
                    "File HDF5:  <a href='" + url_hdf5 + "'>" + filename_hdf5 + "</a>Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, path, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        log = MessageLog()
        log.title = "Export raw data"
        log.message = "Status: error, Task: " + task_id + ", User: " + User.objects.get(
            id=user_id).username + ", Exception: " + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)


@celery.task(base=ExportRawDataCallbackTask, bind=True)
def export_raw_data(self, user_id, compendium_id, path, channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id

    os.makedirs(path, exist_ok=True)
    millis = int(round(time.time() * 1000))
    base_dir = AdminOptions.objects.get(option_name='raw_data_directory').option_value
    file_path_hdf5 = 'export_data_' + str(task_id) + '_' + str(millis) + '.hdf5'
    file_path_tsv = 'export_data_' + str(task_id) + '_' + str(millis) + '.tsv'
    file_path_gz = 'export_data_' + str(task_id) + '_' + str(millis) + '.tsv.gz'
    full_path_hdf5 = os.path.join(path, file_path_hdf5)
    full_path_tsv = os.path.join(path, file_path_tsv)
    full_path_gz = os.path.join(path, file_path_gz)
    try:
        for fl in glob.glob(path + '/*.tsv'):
            os.remove(fl)
        for fl in glob.glob(path + '/*.hdf5'):
            os.remove(fl)
        for fl in glob.glob(path + '/*.gz'):
            os.remove(fl)
    except Exception as e:
        pass
    store = pd.HDFStore(full_path_hdf5)
    header = Sample.objects.using(compendium.compendium_nick_name).\
        order_by('platform', 'experiment').values('id', 'sample_name')
    bio_features = BioFeature.objects.using(compendium.compendium_nick_name). \
        order_by('name')
    bio_feature_name = compendium.compendium_type.bio_feature_name
    reporter_name = 'reporter ({})'.format(','.join(
        [plt.platform_type.description for plt in Platform.objects.using(compendium.compendium_nick_name).all() if plt.platform_type]
    ))
    columns = [bio_feature_name, reporter_name] + ['Platform', 'Platform type'] + [s['sample_name'] for s in header]
    max_sample_name = max([len(s['sample_name']) for s in header])
    min_size = {s['sample_name']: max_sample_name for s in header}
    min_size['Platform'] = max(
            [len(plt.platform_access_id) for plt in Platform.objects.using(compendium.compendium_nick_name)]
        )
    min_size['Platform type'] = max(
            [len(plt.description) for plt in PlatformType.objects.using(compendium.compendium_nick_name)]
    )
    df = pd.DataFrame(columns=columns)
    store.put('raw_data', df, format='table', data_columns=True,
              min_itemsize=min_size)
    line_number = 50000
    batch_size = int((line_number * bio_features.count()) / BioFeatureReporter.objects.using(compendium.compendium_nick_name).count())
    for start, end, total, qs in batch_qs(bio_features, batch_size=batch_size):
        bfr = {(bf.id, bf.name): list(bf.biofeaturereporter_set.order_by('platform').values_list('id', 'name',
            'platform__platform_access_id', 'platform__platform_type__description')) for bf in qs}
        bf_name_len = 15
        rep_name_len = 15
        data = [
            [],  # bio_features
            [],  # reporters
            [],  # platforms
            []   # platform types
        ]
        for k, v in bfr.items():
            for r in v:
                data[0].append(k[1])  # bio_features
                data[1].append(r[0])  # reporters
                data[2].append(r[2])  # platforms
                data[3].append(r[3])  # platform types
                bf_name_len = max(bf_name_len, len(k[1]))
                rep_name_len = max(rep_name_len, len(r[1]))
        min_size[bio_feature_name] = bf_name_len
        min_size[reporter_name] = rep_name_len
        for sample in header:
            rd = {rdv['bio_feature_reporter_id']: rdv['value'] for rdv in
                  RawData.objects.using(compendium.compendium_nick_name).filter(
                      sample__id=sample['id'],
                      bio_feature_reporter_id__in=data[1]
                  ).values('bio_feature_reporter_id', 'value')}
            data.append([rd.get(r, np.nan) for r in data[1]])
        reporters_map = dict([y[:2] for x in bfr.values() for y in x])
        data[1] = [reporters_map[i] for i in data[1]]  # use name instead of id for reporters
        store.append('raw_data', pd.DataFrame(np.array(data).T, columns=columns),
                     format='table', data_columns=True,
                     min_itemsize=min_size)
    store.close()
    header_flag = True
    with open(full_path_tsv, 'a') as f:
        for df in pd.read_hdf(full_path_hdf5, chunksize=line_number):
            df.to_csv(f, header=header_flag, sep='\t', index=False)
            header_flag = False

    compress_gz(full_path_tsv, full_path_gz)

    return full_path_gz.replace(base_dir, '')



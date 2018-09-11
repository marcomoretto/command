import json
import os
import subprocess

import celery
from Bio.Blast.Applications import NcbiblastnCommandline
from celery.contrib.abortable import AbortableTask
from channels import Group, Channel
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connections, DatabaseError

from command.lib.coll.platform.microarray_mapper import MicroarrayMapper
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.view_task import ViewTask
from command.lib.utils.message import Message
from command.models import init_database_connections


class RunPlatformMapperCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, plt_dir, platform_id, use_short_blastn, alignment_identity, \
            channel_name, view, operation = args

        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=platform_id)
        log = MessageLog()
        log.title = "Alignment of platform " + platform.platform_access_id
        log.message = "Status: success, Platform: " + platform.platform_access_id + ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username + ", Report: " + retval
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        blast_file_name = os.path.join(plt_dir, task_id + '.blast')
        mapper = MicroarrayMapper(blast_file_name)
        mapper.set_alignment_status('ready')

        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        # remove files
        for file in [f for f in os.listdir(plt_dir) if
                     os.path.isfile(os.path.join(plt_dir, f)) and f.startswith(task_id)]:
            if file.endswith('.sqlite') or file.endswith('.blast'):
                continue
            os.remove(os.path.join(plt_dir, file))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, plt_dir, platform_id, use_short_blastn, alignment_identity, \
            channel_name, view, operation = args
        channel = Channel(channel_name)
        message = Message(type='error', title='Error', message=str(exc))
        message.send_to(channel)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=platform_id)
        log = MessageLog()
        log.title = "Alignment of platform " + platform.platform_access_id
        log.message = "Status: error, Platform: " + platform.platform_access_id + \
                      ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                      "Exception: " + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        blast_file_name = os.path.join(plt_dir, task_id + '.blast')
        mapper = MicroarrayMapper(blast_file_name)
        mapper.set_alignment_status('error')

        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })

        # remove files
        for file in [f for f in os.listdir(plt_dir) if
                     os.path.isfile(os.path.join(plt_dir, f)) and f.startswith(task_id)]:
            if file.endswith('.sqlite') or file.endswith('.blast'):
                continue
            os.remove(os.path.join(plt_dir, file))


class RunAlignmentFilterCallbackTask(AbortableTask, celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, plt_dir, platform_id, blast_file_name, alignment_length_1, gap_open_1, \
            mismatches_1, alignment_length_2, gap_open_2, mismatches_2, channel_name, view, operation = args
        Group("compendium_" + str(compendium_id)).send({
            'text': json.dumps({
                'stream': view,
                'payload': {
                    'request': {'operation': 'refresh'},
                    'data': None
                }
            })
        })
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=platform_id)
        mapper = MicroarrayMapper(os.path.join(plt_dir, blast_file_name))
        mapper.set_filter_status(retval, 'ready')
        log = MessageLog()
        log.title = "Filtering of alignment" + blast_file_name
        log.message = "Status: success, Platform: " + platform.platform_access_id + ", Alignment: " + blast_file_name + \
                      ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, plt_dir, platform_id, blast_file_name, alignment_length_1, gap_open_1, \
            mismatches_1, alignment_length_2, gap_open_2, mismatches_2, channel_name, view, operation = args
        channel = Channel(channel_name)
        message = Message(type='error', title='Error', message=str(exc))
        message.send_to(channel)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        platform = Platform.objects.using(compendium.compendium_nick_name).get(id=platform_id)
        log = MessageLog()
        log.title = "Filtering of alignment " + blast_file_name
        log.message = "Status: error, Platform: " + platform.platform_access_id + ", Alignment: " + blast_file_name + \
                      ", Task: " + task_id + ", User: " + User.objects.get(id=user_id).username +\
                      "Exception: " + str(exc) + ", Stacktrace: " + einfo.traceback
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)


@celery.task(base=RunAlignmentFilterCallbackTask, bind=True)
def run_alignment_filter(self, user_id, compendium_id, plt_dir, platform_id, blast_file_name,
                        alignment_length_1, gap_open_1, mismatches_1, alignment_length_2, gap_open_2, mismatches_2,
                        channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id
    mapper = MicroarrayMapper(os.path.join(plt_dir, blast_file_name))
    filter_params_id = mapper.write_params_db(float(alignment_length_1), float(gap_open_1), float(mismatches_1),
                  float(alignment_length_2), float(gap_open_2), float(mismatches_2))
    mapper.set_filter_status(filter_params_id, 'running')
    task_id = self.request.id
    try:
        ViewTask.objects.using(compendium.compendium_nick_name). \
            get(view=view, operation=operation).delete()
    except Exception as e:
        pass
    channel_task = ViewTask(task_id=task_id, operation=operation, view=view)
    channel_task.save(using=compendium.compendium_nick_name)

    Group("compendium_" + str(compendium_id)).send({
        'text': json.dumps({
            'stream': view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })

    try:
        mapper.filter(filter_params_id, self.is_aborted)
        if self.is_aborted():
            raise DatabaseError('Operation aborted by user')
    except Exception as e:
        mapper.set_filter_status(filter_params_id, 'error')
        raise e

    return filter_params_id


@celery.task(base=RunPlatformMapperCallbackTask, bind=True)
def run_platform_mapper(self, user_id, compendium_id, plt_dir, platform_id, use_short_blastn, alignment_identity, channel_name, view, operation):
    init_database_connections()
    user = User.objects.get(id=user_id)
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    task_id = self.request.id

    blast_file_name = os.path.join(plt_dir, task_id + '.blast')
    open(blast_file_name, 'a').close()
    mapper = MicroarrayMapper(blast_file_name)
    mapper.create_db(alignment_identity, use_short_blastn)
    mapper.set_alignment_status('running')

    Group("compendium_" + str(compendium_id)).send({
        'text': json.dumps({
            'stream': view,
            'payload': {
                'request': {'operation': 'refresh'},
                'data': None
            }
        })
    })

    report = ''

    # create gene fasta file (bio_feature)
    gene_file_name = os.path.join(plt_dir, task_id + '_gene.fasta')
    with open(gene_file_name, 'w') as f:
        gene_name = ''
        for gene in BioFeature.objects.using(compendium.compendium_nick_name).all():
            try:
                gene_name = gene.name
                sequence = gene.biofeaturevalues_set.filter(bio_feature_field__name='sequence')[0].value
                f.write('>' + str(gene.id) + '\n' + str(sequence) + '\n')
            except Exception as e:
                report += 'You have no sequence for ' + gene_name + '<br>'

    # create probe fasta file
    probe_file_name = os.path.join(plt_dir, task_id + '_probe.fasta')
    with open(probe_file_name, 'w') as f:
        probe_name = ''
        for probe in BioFeatureReporter.objects.using(compendium.compendium_nick_name).\
                filter(platform_id=platform_id).all():
            try:
                probe_name = probe.name
                sequence = probe.biofeaturereportervalues_set.filter(
                    bio_feature_reporter_field__name='sequence')[0].value
                f.write('>' + str(probe.id) + '\n' + str(sequence) + '\n')
            except Exception as e:
                report += 'You have no sequence for ' + probe_name + '<br>'

    # create blast db
    cmd = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'ncbi-blast', 'bin')
    cmd += '/makeblastdb -dbtype nucl -in ' + gene_file_name
    process = subprocess.Popen(cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  shell=True)
    (out, err) = process.communicate()

    # do alignment
    cmd = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'ncbi-blast', 'bin')
    os.environ["PATH"] += os.pathsep + cmd
    outfmt = '\'6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen\''
    blastn_cline = NcbiblastnCommandline(query=probe_file_name, db=gene_file_name,
                                         perc_identity=alignment_identity / 100.0, outfmt=outfmt,
                                         out=blast_file_name)
    if use_short_blastn:
        blastn_cline = NcbiblastnCommandline(query=probe_file_name, db=gene_file_name,
                                         perc_identity=alignment_identity / 100.0, task='blastn-short', outfmt=outfmt,
                                         out=blast_file_name)
    (out, err) = blastn_cline()

    # create stats db
    mapper.create_db(alignment_identity, use_short_blastn)

    os.chmod(mapper.blast_filename, 0o666)
    os.chmod(mapper.sqlite_filename, 0o666)

    return report

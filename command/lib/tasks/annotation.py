from __future__ import absolute_import, unicode_literals

import datetime
import json
import os

import celery
from channels import Channel, Group
from django.contrib.auth.models import User

from command.lib.anno.annotation_parser import BaseAnnotationParser
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.annotation_value import AnnotationValue
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_annotation import BioFeatureAnnotation
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.ontology import Ontology
from command.lib.db.compendium.ontology_node import OntologyNode
from command.lib.utils.message import Message
from command.lib.utils.queryset_iterator import chunks


class AnnotationCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, ontology_id, filename, file_type, channel_name, view, operation = args

        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)

        log = MessageLog()
        log.title = "Biological feature annotation"
        log.message = "Status: success, Task: " + task_id + ", User: " + User.objects.get(
            id=user_id).username
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        message = Message(type='info', title=log.title, message='Annotation has been correctly imported')
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

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        user_id, compendium_id, ontology_id, filename, file_type, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)

        log = MessageLog()
        log.title = "Biological feature annotation"
        log.message = "Status: error, Task: " + task_id + ", User: " + User.objects.get(
            id=user_id).username + ", Error: " + str(exc)
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        message = Message(type='error', title='Error', message=str(exc))
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


@celery.task(base=AnnotationCallbackTask, bind=True)
def annotation_task(self, user_id, compendium_id, ontology_id, filename, file_type, channel_name, view, operation):
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    ontology = Ontology.objects.using(compendium.compendium_nick_name).get(id=ontology_id)
    cls = [cls for cls in BaseAnnotationParser.get_parser_classes() if cls.FILE_TYPE_NAME == file_type][0]
    parser = cls()
    bf_map = dict(BioFeature.objects.using(compendium.compendium_nick_name).values_list('name', 'id'))
    ann_map = dict(OntologyNode.objects.using(compendium.compendium_nick_name).filter(ontology=ontology).values_list('original_id', 'id'))
    for chunk in parser.parse(filename):
        annotations = []
        annotation_values = []
        for ann in chunk:
            if ann[0] in bf_map and ann[1] in ann_map:
                ann_val = AnnotationValue(
                    ontology_node_id=ann_map[ann[1]],
                    value='True',
                    value_type='boolean'
                )
                annotation_values.append(ann_val)
        AnnotationValue.objects.using(compendium.compendium_nick_name).bulk_create(annotation_values)
        annotation_values_map = dict(AnnotationValue.objects.using(compendium.compendium_nick_name).filter(ontology_node__ontology=ontology).
                                     values_list('ontology_node_id', 'id')
                                     )
        for ann in chunk:
            if ann[0] in bf_map and ann[1] in ann_map:
                bfa = BioFeatureAnnotation()
                bfa.bio_feature_id = bf_map[ann[0]]
                bfa.annotation_value_id = annotation_values_map[ann_map[ann[1]]]
                annotations.append(bfa)
        BioFeatureAnnotation.objects.using(compendium.compendium_nick_name).bulk_create(annotations)









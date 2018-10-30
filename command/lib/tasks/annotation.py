from __future__ import absolute_import, unicode_literals

import datetime
import json
import os

import celery
from channels import Channel, Group

from command.lib.anno.annotation_parser import BaseAnnotationParser
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_annotation import BioFeatureAnnotation
from command.lib.db.compendium.ontology import Ontology
from command.lib.db.compendium.ontology_node import OntologyNode
from command.lib.utils.queryset_iterator import chunks


class AnnotationCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        pass


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
        for ann in chunk:
            bfa = BioFeatureAnnotation()
            if ann[0] in bf_map and ann[1] in ann_map:
                bfa.bio_feature_id = bf_map[ann[0]]
                bfa.ontology_node_id = ann_map[ann[1]]
                annotations.append(bfa)
        BioFeatureAnnotation.objects.using(compendium.compendium_nick_name).bulk_create(annotations)









from __future__ import absolute_import, unicode_literals

import datetime
import json
import os
from time import sleep

import celery
from channels import Channel, Group
from django.contrib.auth.models import User

from command.lib.anno.base_parser import BaseParser
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.message_log import MessageLog
from command.lib.db.compendium.ontology import Ontology
from command.lib.db.compendium.ontology_edge import OntologyEdge
from command.lib.db.compendium.ontology_node import OntologyNode
from command.lib.utils.message import Message
from command.lib.utils.queryset_iterator import chunks
from command.models import init_database_connections


class CreateOntologyCallbackTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        user_id, compendium_id, ontology_name, ontology_description, destination, fields_json, filename, file_type, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)

        log = MessageLog()
        log.title = "Create ontology"
        log.message = "Status: success, Ontology: " + ontology_name + ", Task: " + task_id + ", User: " + User.objects.get(
            id=user_id).username
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        message = Message(type='info', title=log.title, message='Ontology ' + ontology_name + ' has been created.')
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
        user_id, compendium_id, ontology_name, ontology_description, destination, fields_json, filename, file_type, channel_name, view, operation = args
        channel = Channel(channel_name)
        compendium = CompendiumDatabase.objects.get(id=compendium_id)

        log = MessageLog()
        log.title = "Create ontology"
        log.message = "Status: error, Ontology: " + ontology_name + ", Task: " + task_id + ", User: " + User.objects.get(
            id=user_id).username + ", Error: " + str(exc)
        log.source = log.SOURCE[1][0]
        log.save(using=compendium.compendium_nick_name)

        message = Message(type='error', title=log.title, message=str(exc))
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


@celery.task(base=CreateOntologyCallbackTask, bind=True)
def create_ontology_task(self, user_id, compendium_id, ontology_name,
                         ontology_description, destination, fields_json, filename, file_type,
                         channel_name, view, operation):
    compendium = CompendiumDatabase.objects.get(id=compendium_id)
    ontology = Ontology()
    ontology.creation_date = datetime.date.today()
    if filename:
        ontology.original_filename = os.path.basename(filename)
    ontology.name = ontology_name
    ontology.description = ontology_description
    ontology.is_biofeature = 'biofeature' in destination
    ontology.is_sample = 'sample' in destination
    ontology.json = fields_json
    ontology.save(using=compendium.compendium_nick_name)
    if filename and file_type:
        cls = [cls for cls in BaseParser.get_parser_classes() if cls.FILE_TYPE_NAME == file_type][0]
        parser = cls(compendium.compendium_nick_name)
        structure = parser.parse(filename)
        for c in chunks(structure['elements']['nodes'], 1000):
            nodes = []
            for n in c:
                node = OntologyNode()
                node.ontology = ontology
                node.original_id = n['data']['id']
                node.json = n['data']
                if not ontology.json or 'columns' not in ontology.json:
                    ontology.json = {'columns': [{'text': x.title().replace('_', ' '), 'data_index': x} for x in n['data'].keys() if x != 'id']}
                    ontology.save(using=compendium.compendium_nick_name)
                nodes.append(node)
            OntologyNode.objects.using(compendium.compendium_nick_name).bulk_create(nodes)
        node_ids = dict(OntologyNode.objects.using(compendium.compendium_nick_name).filter(ontology=ontology).values_list('original_id', 'id'))
        for c in chunks(structure['elements']['edges'], 10000):
            edges = []
            for e in c:
                edge = OntologyEdge()
                edge.source_id = node_ids[e['data']['source']]
                edge.target_id = node_ids[e['data']['target']]
                edge.is_directed = True
                edge.ontology = ontology
                edge.edge_type = e['data']['key']
                edges.append(edge)
            OntologyEdge.objects.using(compendium.compendium_nick_name).bulk_create(edges)








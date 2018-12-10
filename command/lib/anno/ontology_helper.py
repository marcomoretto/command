from django.db.models import Q

from command.lib.db.compendium.ontology import Ontology
from command.lib.db.compendium.ontology_edge import OntologyEdge
from command.lib.db.compendium.ontology_node import OntologyNode


class OntologyHelper:

    def __init__(self, compendium, ontology_name):
        self.compendium = compendium
        self.ontology_name = ontology_name

    def get_neighbourhood(self, node_id, level=1):
        ontology = Ontology.objects.using(self.compendium).get(name=self.ontology_name)
        if not node_id:
            node = OntologyNode.objects.using(self.compendium).filter(ontology=ontology).first()
        else:
            node = OntologyNode.objects.using(self.compendium).get(ontology=ontology, id=node_id)
        node_ids = [node.id] if node else []
        edges = []
        nodes = []
        nodes_qr = []
        edges_qr = []
        for lvl in range(level):
            nodes_qr = OntologyNode.objects.using(self.compendium).filter(ontology=ontology, id__in=node_ids)
            edges_qr = OntologyEdge.objects.using(self.compendium).filter(Q(source_id__in=node_ids) | Q(target_id__in=node_ids))
            node_ids = list(set([y for x in edges_qr.values_list('source', 'target') for y in x]))
            edges_qr = OntologyEdge.objects.using(self.compendium).filter(
                Q(source_id__in=node_ids) & Q(target_id__in=node_ids))
        for e in edges_qr:
            edges.append({'data': {
                'id': 'edge_' + str(e.id),
                'source': e.source.id,
                'target': e.target.id
            }})
            nodes.append({'data': {**e.target.json, **{'id': e.target.id, 'original_id': e.target.original_id}}})
            nodes.append({'data': {**e.source.json, **{'id': e.source.id, 'original_id': e.source.original_id}}})
        if node:
            nodes = [{'data': {**node.json, **{'id': node.id, 'original_id': node.original_id}}}] + nodes
        return {
            'nodes': nodes,
            'edges': edges
        }

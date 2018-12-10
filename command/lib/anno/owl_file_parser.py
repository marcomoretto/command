
import networkx
from onto2nx import OWLParser, parse_owl

from command.lib.anno.base_parser import BaseParser


class OWLFileParser(BaseParser):
    FILE_TYPE_NAME = 'OWL'

    def parse(self, filename):
        graph = parse_owl(filename)
        return networkx.readwrite.cytoscape_data(graph)

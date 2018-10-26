
import networkx
import obonet

from command.lib.anno.base_parser import BaseParser


class OBOFileParser(BaseParser):
    FILE_TYPE_NAME = 'OBO'

    def parse(self, filename):
        graph = obonet.read_obo(filename)
        return networkx.readwrite.cytoscape_data(graph)

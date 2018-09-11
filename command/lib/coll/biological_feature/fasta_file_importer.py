from Bio import SeqIO
from django.db import transaction

from command.lib.coll.biological_feature.base_importer import BaseImporter
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_fields import BioFeatureFields
from command.lib.db.compendium.bio_feature_values import BioFeatureValues


class FastaFileImporter(BaseImporter):
    FILE_TYPE_NAME = 'FASTA'

    def parse(self, filename):
        sequence_field = BioFeatureFields.objects.using(self.compendium).get(name='sequence')
        with transaction.atomic(using=self.compendium):
            with open(filename, 'rU') as handle:
                for record in SeqIO.parse(handle, 'fasta'):
                    gene = BioFeature()
                    gene.name = record.id
                    gene.description = record.description
                    gene.save(using=self.compendium)
                    bf_value = BioFeatureValues()
                    bf_value.bio_feature = gene
                    bf_value.bio_feature_field = sequence_field
                    bf_value.value = str(record.seq)
                    bf_value.save(using=self.compendium)

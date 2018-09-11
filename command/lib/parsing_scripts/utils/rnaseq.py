from command.lib.coll.rnaseq.trimmomatic import Trimmomatic
from command.lib.coll.rnaseq.kallisto import Kallisto
from command.lib.db.compendium.bio_feature import BioFeature


def create_fasta(file, compendium):
    with open(file, 'w') as f:
        for gene in BioFeature.objects.using(compendium).all():
            try:
                sequence = gene.biofeaturevalues_set.filter(bio_feature_field__name='sequence')[0].value
                f.write('>' + str(gene.name) + '\n' + str(sequence) + '\n')
            except Exception as e:
                pass
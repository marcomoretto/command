from django.conf import settings
from django.core.management.base import BaseCommand

from command.lib.db.admin.bio_feature_fields_admin import BioFeatureFieldsAdmin
from command.lib.db.admin.bio_feature_reporter_fields_admin import BioFeatureReporterFieldsAdmin
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.admin.compendium_type import CompendiumType
from command.lib.db.admin.platform_type_admin import PlatformTypeAdmin
from command.lib.utils import init_compendium


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        try:
            compendium_name = 'demo'
            if options['name']:
                compendium_name = options['name']
            print('Creating demo compendium')
            try:
                # Compendium type gene expression
                compendium_type_ge = CompendiumType()
                compendium_type_ge.name = 'gene_expression'
                compendium_type_ge.description = 'Gene expression compendium'
                compendium_type_ge.bio_feature_name = 'gene'
                compendium_type_ge.save()
                # Platform type microarray
                plt_type = PlatformTypeAdmin()
                plt_type.name = 'microarray'
                plt_type.description = 'MicroArray'
                plt_type.bio_feature_reporter_name = 'probe'
                plt_type.compendium_type = compendium_type_ge
                plt_type.save()
                # Bio Feature reporter fields
                probe_access_id = BioFeatureReporterFieldsAdmin()
                probe_access_id.description = 'Probe access id'
                probe_access_id.name = 'probe_access_id'
                probe_access_id.feature_type = 'string'
                probe_access_id.platform_type = plt_type
                probe_access_id.save()
                probe_set_name = BioFeatureReporterFieldsAdmin()
                probe_set_name.description = 'Probeset name'
                probe_set_name.name = 'probe_set_name'
                probe_set_name.feature_type = 'string'
                probe_set_name.platform_type = plt_type
                probe_set_name.save()
                probe_type = BioFeatureReporterFieldsAdmin()
                probe_type.description = 'Probe type'
                probe_type.name = 'probe_type'
                probe_type.feature_type = 'string'
                probe_type.platform_type = plt_type
                probe_type.save()
                probe_sequence = BioFeatureReporterFieldsAdmin()
                probe_sequence.description = 'Probe sequence'
                probe_sequence.name = 'sequence'
                probe_sequence.feature_type = 'string'
                probe_sequence.platform_type = plt_type
                probe_sequence.save()
                # Platform type rnaseq
                plt_type = PlatformTypeAdmin()
                plt_type.name = 'rnaseq'
                plt_type.description = 'RNA-seq'
                plt_type.bio_feature_reporter_name = 'read'
                plt_type.compendium_type = compendium_type_ge
                plt_type.save()
                # Bio Feature fields
                gene_sequence = BioFeatureFieldsAdmin()
                gene_sequence.compendium_type = compendium_type_ge
                gene_sequence.feature_type = 'string'
                gene_sequence.name = 'sequence'
                gene_sequence.description = 'Gene nucleotide sequence'
                gene_sequence.save()
            except Exception as e:
                compendium_type_ge = CompendiumType.objects.get(name='gene_expression')
            # Demo compendium
            demo = CompendiumDatabase()
            demo.compendium_name = compendium_name
            demo.compendium_nick_name = compendium_name
            demo.description = 'Demo compendium'
            demo.html_description = 'Demo compendium'
            demo.compendium_type = compendium_type_ge
            demo.db_engine = settings.DATABASES['default']['ENGINE']
            demo.db_user = settings.DATABASES['default']['USER']
            demo.db_password = settings.DATABASES['default']['PASSWORD']
            demo.db_port = settings.DATABASES['default']['PORT']
            demo.db_host = settings.DATABASES['default']['HOST']
            demo.save()
            init_compendium.init_compendium(demo.id)
        except Exception as e:
            print(str(e))

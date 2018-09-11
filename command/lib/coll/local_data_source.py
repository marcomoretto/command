import os

import yaml
from django.db import transaction

from command.lib.coll.experiment_data_collection_manager import ExperimentDataCollectionManager
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.data_source import DataSource
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.utils import file_system


class LocalDataSource(ExperimentDataCollectionManager):

    def __init__(self):
        ExperimentDataCollectionManager.__init__(self)

    @property
    def experiment_structure_filename(self):
        return "experiment_structure.yml"

    @property
    def experiment_accession_base_link(self):
        return ""

    @property
    def platform_accession_base_link(self):
        return ""

    @property
    def scientific_paper_accession_base_link(self):
        return ""

    def uncompress_experiment_file(self, exp_file, out_dir):
        file_system.uncompress_file(exp_file, out_dir)

    def create_experiment_structure(self, compendium_id, experiment_id, out_dir):
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        local_data_source = DataSource.objects.using(compendium.compendium_nick_name).get(source_name='local')
        with open(os.path.join(out_dir, self.experiment_structure_filename)) as f:
            exp_struct = yaml.load(f)

        new_platforms = {}
        for plt, samples in exp_struct['experiment'].items():
            platform = Platform()
            try:
                platform = Platform.objects.using(compendium.compendium_nick_name). \
                    get(platform_access_id=plt)
            except Exception as e:
                platform.platform_access_id = plt
                platform.data_source = local_data_source
            new_platforms[platform.platform_access_id] = platform

        with transaction.atomic(using=compendium.compendium_nick_name):
            data_ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_data_ready')
            exp = Experiment()
            exp.experiment_access_id = experiment_id
            exp.status = data_ready_status
            exp.data_source = local_data_source
            exp.save(using=compendium.compendium_nick_name)
            samples = []
            for pl_id, pl in new_platforms.items():
                pl.save(using=compendium.compendium_nick_name)
                for smp in exp_struct['experiment'][pl_id]['samples']:
                    sample = Sample()
                    sample.sample_name = smp
                    sample.experiment = exp
                    sample.platform = pl
                    samples.append(sample)

            Sample.objects.using(compendium.compendium_nick_name).bulk_create(samples)

import importlib

import time
from django.db import OperationalError

from command.lib.db.parsing.parsing_experiment import ParsingExperiment
from command.models import init_parsing_database_connections


class ExperimentProxy:

    def __init__(self, exp, db):
        self.db = db
        module_name, class_name = '.'.join(exp.data_source.python_class.split('.')[:-1]), \
                                  exp.data_source.python_class.split('.')[-1]
        python_class = getattr(importlib.import_module(module_name), class_name)()

        self.organism = None
        self.experiment_access_id = None
        self.experiment_name = None
        self.scientific_paper_ref = None
        self.description = None
        self.exp_id = exp.id
        self.scientific_paper_accession_base_link = python_class.scientific_paper_accession_base_link

    def save_experiment_object(self):
        init_parsing_database_connections(self.db)
        try:
            parsing_exp = ParsingExperiment.objects.using(self.db).get(experiment_fk=self.exp_id)
        except Exception as e:
            parsing_exp = ParsingExperiment()
        saved = False
        while not saved:
            try:
                parsing_exp.organism = self.organism if self.organism is not None else parsing_exp.organism
                parsing_exp.experiment_access_id = self.experiment_access_id if self.experiment_access_id is not None else parsing_exp.experiment_access_id
                parsing_exp.experiment_name = self.experiment_name if self.experiment_name is not None else parsing_exp.experiment_name
                parsing_exp.scientific_paper_ref = self.scientific_paper_accession_base_link + self.scientific_paper_ref \
                    if self.scientific_paper_ref is not None else parsing_exp.scientific_paper_ref
                parsing_exp.description = self.description if self.description is not None else parsing_exp.description
                parsing_exp.experiment_fk = self.exp_id
                parsing_exp.save(using=self.db)
                saved = True
            except OperationalError as e:
                time.sleep(2)

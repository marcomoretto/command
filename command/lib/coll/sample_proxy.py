import time
from django.db import transaction, OperationalError

from command.lib.db.parsing.parsing_raw_data import ParsingRawData
from command.lib.db.parsing.parsing_sample import ParsingSample
from command.models import init_parsing_database_connections


class SampleProxy:

    def __init__(self, smp, db):
        self.db = db
        self.sample_name = None
        self.description = None
        self.smp_id = smp.id
        self.buffer = []
        self.buffer_size = 2000

        init_parsing_database_connections(self.db)
        try:
            self.parsing_smp = ParsingSample.objects.using(self.db).get(sample_fk=self.smp_id)
        except Exception as e:
            self.parsing_smp = ParsingSample()
        self.parsing_smp.sample_name = smp.sample_name
        self.parsing_smp.description = smp.description
        self.parsing_smp.reporter_platform = self.parsing_smp.platform.reporter_platform
        saved = False
        while not saved:
            try:
                self.parsing_smp.save(using=self.db)
                saved = True
            except OperationalError as e:
                time.sleep(2)
        saved = False
        while not saved:
            try:
                self.parsing_smp.parsingrawdata_set.all().delete()
                saved = True
            except OperationalError as e:
                time.sleep(2)

    def add_raw_data(self, bio_feature_reporter, value):
        if len(self.buffer) >= self.buffer_size:
            saved = False
            while not saved:
                try:
                    init_parsing_database_connections(self.db)
                    with transaction.atomic(using=self.db):
                        ParsingRawData.objects.using(self.db).bulk_create(
                            self.buffer
                        )
                    self.buffer.clear()
                    saved = True
                except OperationalError as e:
                    time.sleep(2)
        else:
            self.buffer.append(
                ParsingRawData(sample=self.parsing_smp,
                                bio_feature_reporter_name=bio_feature_reporter,
                                value=value)
            )

    def save_sample_object(self):
        saved = False
        while not saved:
            try:
                init_parsing_database_connections(self.db)
                parsing_smp = ParsingSample.objects.using(self.db).get(sample_fk=self.smp_id)
                parsing_smp.sample_name = self.sample_name if self.sample_name is not None else parsing_smp.sample_name
                parsing_smp.description = self.description if self.description is not None else parsing_smp.description
                parsing_smp.sample_fk = self.smp_id
                parsing_smp.save(using=self.db)

                with transaction.atomic(using=self.db):
                    ParsingRawData.objects.using(self.db).bulk_create(
                        self.buffer
                    )
                saved = True
            except OperationalError as e:
                time.sleep(2)

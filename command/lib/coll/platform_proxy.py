import time
from django.db import transaction, OperationalError

from command.lib.db.parsing.parsing_bio_feature_reporter import ParsingBioFeatureReporter
from command.lib.db.parsing.parsing_bio_feature_reporter_values import ParsingBioFeatureReporterValues
from command.lib.db.parsing.parsing_platform import ParsingPlatform
from command.models import init_parsing_database_connections


class PlatformProxy:

    def __init__(self, plt, db):
        self.db = db
        self.platform_access_id = None
        self.platform_name = None
        self.description = None
        self.platform_type = None
        self.plt_id = plt.id
        self.bio_feature_reporter_buffer = []
        self.bio_feature_reporter_buffer_size = 2000

        init_parsing_database_connections(self.db)
        try:
            parsing_plt = ParsingPlatform.objects.using(self.db).get(platform_fk=self.plt_id)
        except Exception as e:
            parsing_plt = ParsingPlatform()
        parsing_plt.platform_access_id = plt.platform_access_id
        parsing_plt.platform_name = plt.platform_name
        parsing_plt.description = plt.description
        parsing_plt.platform_fk = plt.id
        parsing_plt.platform_type = plt.platform_type.name if plt.platform_type is not None else None
        saved = False
        while not saved:
            try:
                parsing_plt.save(using=self.db)
                saved = True
            except OperationalError as e:
                time.sleep(2)
        saved = False
        while not saved:
            try:
                parsing_plt.parsingbiofeaturereporter_set.all().delete()
                saved = True
            except OperationalError as e:
                time.sleep(2)

    def add_bio_feature_reporter_data(self, name, description, *args, **kwargs):
        if len(self.bio_feature_reporter_buffer) >= self.bio_feature_reporter_buffer_size:
            saved = False
            while not saved:
                try:
                    init_parsing_database_connections(self.db)
                    parsing_plt = ParsingPlatform.objects.using(self.db).get(platform_fk=self.plt_id)
                    with transaction.atomic(using=self.db):
                        for rep, values in self.bio_feature_reporter_buffer:
                            rep.platform = parsing_plt
                            rep.save(using=self.db)
                            for value in values:
                                value.bio_feature_reporter = rep
                                value.save(using=self.db)

                    self.bio_feature_reporter_buffer.clear()
                    saved = True
                except OperationalError as e:
                    time.sleep(2)
        else:
            reporter = ParsingBioFeatureReporter(name=name, description=description)
            values = []
            for field, value in kwargs.items():
                reporter_field_value = ParsingBioFeatureReporterValues(
                    bio_feature_reporter_field=field,
                    value=value
                )
                values.append(reporter_field_value)
            self.bio_feature_reporter_buffer.append((reporter, values))

    def save_platform_object(self):
        saved = False
        while not saved:
            try:
                init_parsing_database_connections(self.db)
                parsing_plt = ParsingPlatform.objects.using(self.db).get(platform_fk=self.plt_id)
                parsing_plt.platform_access_id = self.platform_access_id if self.platform_access_id is not None else parsing_plt.platform_access_id
                parsing_plt.platform_name = self.platform_name if self.platform_name is not None else parsing_plt.platform_name
                parsing_plt.description = self.description if self.description is not None else parsing_plt.description
                parsing_plt.platform_fk = self.plt_id
                parsing_plt.platform_type = self.platform_type
                parsing_plt.save(using=self.db)

                with transaction.atomic(using=self.db):
                    for rep, values in self.bio_feature_reporter_buffer:
                        rep.platform = parsing_plt
                        rep.save(using=self.db)
                        for value in values:
                            value.bio_feature_reporter = rep
                            value.save(using=self.db)
                saved = True
            except OperationalError as e:
                time.sleep(2)

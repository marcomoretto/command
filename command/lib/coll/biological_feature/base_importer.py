from command.lib.db.admin.compendium_database import CompendiumDatabase


class BaseImporter:
    FILE_TYPE_NAME = 'TXT'

    def __init__(self, compendium, bio_feature_name):
        self.compendium = compendium
        self.bio_feature_name = bio_feature_name

    def parse(self, filename):
        raise NotImplementedError('Method not implemented')
from django.db import connections

from command.lib.db.admin.compendium_database import CompendiumDatabase


def init_database_connections():
    try:
        for compendium in CompendiumDatabase.objects.all():
            db_entry = compendium.get_setting_entry()
            connections.databases[db_entry[0]] = db_entry[1]
    except Exception as e:
        pass


def init_parsing_database_connections(key):
    value = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': key,
        'PARSING': True
    }
    connections.databases[key] = value

init_database_connections()

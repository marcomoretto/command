import django.apps
from django.db import connections


class DatabaseRouter(object):
    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'auth' and \
                        obj2._meta.app_label == 'auth':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        dbs = ['default']
        parsing = connections[db].settings_dict.get('PARSING', False)
        models = {m.__name__.lower(): m.__module__ for m in django.apps.apps.get_models()}
        if model_name and 'command.lib.db.compendium' in models[model_name.lower()]:
            return not parsing and db not in dbs
        if model_name and 'command.lib.db.parsing' in models[model_name.lower()]:
            return parsing and db not in dbs
        elif db not in dbs:
            return False
        return None

import importlib
import inspect
import os
import pkgutil


class BaseParser:
    FILE_TYPE_NAME = 'TXT'

    def __init__(self, compendium):
        self.compendium = compendium

    def parse(self, filename):
        raise NotImplementedError('Method not implemented')

    @staticmethod
    def get_parser_classes():
        classes = set()
        path = os.path.dirname(os.path.realpath(__file__))
        pack = path.split('/')
        pack = '.'.join(pack[pack.index('command'):])
        for (module_loader, name, ispkg) in pkgutil.iter_modules([path]):
            module = importlib.import_module(pack + '.' + name)
            for name, cls in inspect.getmembers(module, inspect.isclass):
                for base_cls in cls.__bases__:
                    if base_cls == BaseParser:
                        classes.add(cls)
        return list(classes)
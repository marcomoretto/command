import importlib
import inspect
import os
import pkgutil
import pandas as pd


class BaseAnnotationParser:
    FILE_TYPE_NAME = 'TXT'

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
                    if base_cls == BaseAnnotationParser:
                        classes.add(cls)
        return list(classes)


class CSVFileParser(BaseAnnotationParser):
    FILE_TYPE_NAME = 'CSV'

    def __init__(self):
        self.chunksize = 10000

    def parse(self, filename):
        for chunk in pd.read_csv(filename, chunksize=self.chunksize, sep=',', header=None):
            yield [tuple(x) for x in chunk.values]


class TSVFileParser(BaseAnnotationParser):
    FILE_TYPE_NAME = 'TSV'

    def __init__(self):
        self.chunksize = 10000

    def parse(self, filename):
        for chunk in pd.read_csv(filename, chunksize=self.chunksize, sep='\t', header=None):
            yield [tuple(x) for x in chunk.values]
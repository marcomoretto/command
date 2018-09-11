from collections import OrderedDict

class SoftFile:

    class BaseParser:
        def __init__(self, filename):
            self.parent = None
            self._filename = filename

        def set_parent(self, parent):
            self.parent = parent

        @property
        def table_data(self):
            with open(self._filename) as f:
                f.seek(self.table_begin)
                line = f.readline()
                header = [h.strip() for h in line.split('\t')]
                line = f.readline()
                while line:
                    splitted_line = [l.strip() for l in line.split('\t')]
                    yield dict(zip(header, splitted_line))
                    line = f.readline()
                    if f.tell() == self.table_end:
                        break
            return self._filename

        @staticmethod
        def parse(tokens, cursor, obj):
            if tokens[0].startswith('#'):
                pass
            elif 'table_begin' in tokens[0]:
                setattr(obj, 'table_begin', cursor)
            elif 'table_end' in tokens[0]:
                setattr(obj, 'table_end', cursor)
            elif tokens[0] == SoftFile.SERIES_START:
                obj.name = tokens[1]
            elif hasattr(obj, 'table_end') or not hasattr(obj, 'table_begin'):
                value = tokens[1]
                if hasattr(obj, tokens[0][1:]):
                    tmp = getattr(obj, tokens[0][1:])
                    if isinstance(tmp, list):
                        value = tmp + [value]
                    else:
                        value = [tmp, value]
                setattr(obj, tokens[0][1:], value)
            return obj

    class ParseDatabase(BaseParser):
        pass

    class ParseSeries(BaseParser):
        pass

    class ParsePlatform(BaseParser):
        pass

    class ParseSample(BaseParser):
        pass

    class SoftFileParserException(Exception):
        pass

    DATABASE_START = '^DATABASE'
    SERIES_START = '^SERIES'
    PLATFORM_START = '^PLATFORM'
    SAMPLES_START = '^SAMPLE'

    PARSERS = {
        DATABASE_START: ParseDatabase,
        SERIES_START: ParseSeries,
        PLATFORM_START: ParsePlatform,
        SAMPLES_START: ParseSample
    }

    def __init__(self, filename):
        self.filename = filename
        self.databases = OrderedDict()
        self.series = OrderedDict()
        self.platforms = OrderedDict()
        self.samples = OrderedDict()
        self._cls_to_obj = {
            SoftFile.ParseDatabase: self.databases,
            SoftFile.ParseSeries: self.series,
            SoftFile.ParsePlatform: self.platforms,
            SoftFile.ParseSample: self.samples
        }
        self._cls_to_parent_obj = {
            SoftFile.ParseDatabase: None,
            SoftFile.ParseSeries: self.databases,
            SoftFile.ParsePlatform: self.series,
            SoftFile.ParseSample: self.platforms
        }

    def parse(self):
        current_parser = None
        with open(self.filename) as f:
            line = f.readline()
            i = 0
            while line:
                try:
                    cursor = f.tell()
                    tokens = [tok.strip() for tok in line.split('=')]
                    current_parser, parsed_object = self._parse_tokens(tokens, cursor, current_parser)
                    parent_obj = list(self._cls_to_parent_obj[current_parser].keys())[-1] \
                            if self._cls_to_parent_obj[current_parser] else None
                    parsed_object.set_parent(parent_obj)
                except Exception as e:
                    raise Exception('Error at line: ' + str(i + 1) + " " + str(e))
                line = f.readline()
                i += 1

    def _parse_tokens(self, tokens, cursor, current_parser=None):
        parser = current_parser
        obj_name = None
        if tokens[0] in SoftFile.PARSERS:
            parser = SoftFile.PARSERS[tokens[0]]
            obj_name = tokens[1]
        obj = self._get_object(parser, obj_name)
        return parser, parser.parse(tokens, cursor, obj)

    def _get_object(self, parser, name):
        obj_dict = self._cls_to_obj[parser]
        if name and name not in obj_dict:
            obj_dict[name] = parser(self.filename)
        if not name:
            name = list(obj_dict.keys())[-1]
        return obj_dict[name]

class ADFFileParser(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.header = {}
        self.is_header = True
        self.data_header = []
        self.data_start = None

    @property
    def data(self):
        with open(self.file_name) as f:
            f.seek(self.data_start)
            line = f.readline()
            while line:
                splitted_line = [l.strip() for l in line.strip().split('\t')]
                yield dict(zip(self.data_header, splitted_line))
                line = f.readline()

    def parse(self):
        with open(self.file_name) as f:
            l = f.readline()
            while l:
                if l.strip() == '[main]':
                    self.is_header = False
                    self.data_header = [h.strip() for h in f.readline().strip().split('\t')]
                    self.data_start = f.tell()
                    break
                s = l.strip().split('\t')
                if self.is_header and len(s) > 1:
                    k = s[0].replace('"', '').replace("'", "")
                    v = s[1].replace('"', '').replace("'", "")
                    if k not in self.header:
                        self.header[k] = []
                    self.header[k].append(v)
                l = f.readline()




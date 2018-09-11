class IDFFileParser(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.idf = {}

    def parse(self):
        with open(self.file_name) as f:
            for l in f:
                s = l.strip().split('\t')
                try:
                    self.idf[s[0]] = s[1]   # there should only be one entry for the field (i.e. not multiple tabs!)
                except Exception as e:
                    self.idf[s[0]] = ''

    def get_sdrf_file(self):
        return self.idf['SDRF File']
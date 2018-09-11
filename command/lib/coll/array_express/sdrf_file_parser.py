class SDRFFileParser(object):
    def __init__(self, filename):
        self.filename = filename
        self.sdrf = {}
        self.header = []
        self.assay_name_list = ['Assay Name', 'Hybridization Name']
        self.assay_name = self.assay_name_list[0]

    def parse(self):
        with open(self.filename) as f:
            header = True
            for l in f:
                s = l.strip().split('\t')
                if header:
                    header = False
                    self.header = s
                    for field in self.header:
                        if field in self.assay_name_list:
                            self.assay_name = field
                        self.sdrf[field] = []
                    continue
                for idx in range(len(self.header)):
                    field = self.header[idx]
                    value = s[idx]
                    self.sdrf[field].append(value)

    def get_platforms(self):
        platforms = set()
        for plf in self.sdrf['Array Design REF']:
            platforms.add(plf)
        return list(platforms)

    def get_arrays(self):
        arrays = []
        for arr in self.sdrf[self.assay_name]:
            arrays.append(arr.replace('.', '_'))
        return arrays

    def get_samples(self, platform):
        sample_idxs = []
        for idx in range(len(self.sdrf['Array Design REF'])):
            plf = self.sdrf['Array Design REF'][idx]
            if plf == platform:
                sample_idxs.append(idx)
        samples = set([self.get_arrays()[x] for x in sample_idxs])
        return list(samples)

    def get_array_data_file(self, sample):
        try:
            for idx, adf in enumerate(self.sdrf['Array Data File']):
                if self.sdrf[self.assay_name][idx].replace('.', '_') in sample:
                    return adf
            return ''
        except Exception as e:
            return ''

    def get_number_of_channel(self, sample):
        ch = 0
        for smp in self.get_arrays():
            if smp == sample:
                ch += 1
        return ch

from command.lib.coll.affymetrix.affymetrix_cdf_wrapper import AffyMetrixCdfWrapper


class CdfHeader:

    def __init__(self):
        self.affy = AffyMetrixCdfWrapper()
        self.cdf_header = self.affy._fusionCDFHeaderAutoClass()

    def get_num_probe_sets(self):
        return self.cdf_header.getNumProbeSets()

    def get_num_qc_probe_sets(self):
        return self.cdf_header.getNumQCProbeSets()

    def get_reference(self):
        return self.cdf_header.getReference()

    def get_cols(self):
        return self.cdf_header.getCols()

    def get_rows(self):
        return self.cdf_header.getRows()

    def clear(self):
        self.cdf_header.clear()

    def get_format_version(self):
        return self.cdf_header.getFormatVersion()

    def get_guid(self):
        return self.cdf_header.getGUID()

    def get_integrity_md5(self):
        return self.cdf_header.getIntegrityMd5()

from command.lib.coll.affymetrix.affymetrix_cdf_wrapper import AffyMetrixCdfWrapper


class CdfProbeInformation:

    def __init__(self):
        self.affy = AffyMetrixCdfWrapper()
        self.cdf_probe_information = self.affy._fusionCDFProbeInformationAutoClass()

    def get_list_index(self):
        return self.cdf_probe_information.getListIndex()

    def get_expos(self):
        return self.cdf_probe_information.getExpos()

    def get_x(self):
        return self.cdf_probe_information.getX()

    def get_y(self):
        return self.cdf_probe_information.getY()

    def get_pbase(self):
        self.cdf_probe_information.getPBase()

    def get_tbase(self):
        self.cdf_probe_information.getTBase()

    def get_probe_length(self):
        return self.cdf_probe_information.getProbeLength()

    def get_probe_grouping(self):
        return self.cdf_probe_information.getProbeGrouping()

    def clear(self):
        self.cdf_probe_information.clear()


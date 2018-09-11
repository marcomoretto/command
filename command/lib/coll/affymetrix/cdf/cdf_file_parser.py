from command.lib.coll.affymetrix.affymetrix_cdf_wrapper import AffyMetrixCdfWrapper
from command.lib.coll.affymetrix.cdf.fusion_cdf_header import CdfHeader


class CdfFileParser:

    def __init__(self):
        self.affy = AffyMetrixCdfWrapper()
        self.cdf = self.affy._fusionCDFDataAutoClass()
        self.read_ok = False

    def open_cdf_file(self, file_name):
        j_file_name = self.affy.String(file_name)
        self.set_file_name(j_file_name)
        self.read()

    ####
    # WRAPPER METHODS
    def get_header(self):
        header = CdfHeader()
        header.cdf_header = self.cdf.getHeader()
        return header

    def set_file_name(self, file_name):
        self.cdf.setFileName(file_name)

    def read(self):
        self.read_ok = self.cdf.read()

    def get_probe_set_information(self, index, info):
        self.cdf.getProbeSetInformation(index, info.cdf_probe_set_information)

    def get_probe_set_name(self, index):
        return self.cdf.getProbeSetName(index)

    def get_file_name(self):
        return self.cdf.getFileName()

    def get_error(self):
        return self.cdf.getError()

    def get_chip_type(self):
        return self.cdf.getChipType()

    def prepare_gcos_objects_for_reading(self):
        self.cdf.prepareGCOSObjectsForReading()

    def read_header(self):
        return self.cdf.readHeader()

    def exists(self):
        return self.cdf.exists()

    def is_xda_compatible_file(self):
        return self.cdf.isXDACompatibleFile()

    def get_probe_set_type(self, index):
        return self.cdf.getProbeSetType(index)

    def clear(self):
        self.cdf.clear()

    def get_chip_types(self):
        return self.cdf.getChipTypes()

    def get_guid(self):
        return self.cdf.getGUID()

    def get_integrity_md5(self):
        return self.cdf.getIntegrityMd5()
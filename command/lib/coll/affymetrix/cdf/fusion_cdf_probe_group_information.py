from command.lib.coll.affymetrix.affymetrix_cdf_wrapper import AffyMetrixCdfWrapper


class CdfProbeGroupInformation:

    def __init__(self):
        self.affy = AffyMetrixCdfWrapper()
        self.cdf_probe_group_information = self.affy._fusionCDFProbeGroupInformationAutoClass()

    def get_num_lists(self):
        return self.cdf_probe_group_information.getNumLists()

    def get_num_cells(self):
        return self.cdf_probe_group_information.getNumCells()

    def get_start(self):
        return self.cdf_probe_group_information.getStart()

    def get_stop(self):
        return self.cdf_probe_group_information.getStop()

    def get_probe_set_index(self):
        return self.cdf_probe_group_information.getProbeSetIndex()

    def get_group_index(self):
        return self.cdf_probe_group_information.getGroupIndex()

    def get_name(self):
        return self.cdf_probe_group_information.getName()

    def get_num_cells_per_list(self):
        return self.cdf_probe_group_information.getNumCellsPerList()

    def get_direction(self):
        return self.cdf_probe_group_information.getDirection()

    def get_wobble_situation(self):
        return self.cdf_probe_group_information.getWobbleSituation()

    def get_allele_code(self):
        return self.cdf_probe_group_information.getAlleleCode()

    def get_channel(self):
        return self.cdf_probe_group_information.getChannel()

    def get_rep_type(self):
        return self.cdf_probe_group_information.getRepType()

    def get_cell(self, index, probe):
        self.cdf_probe_group_information.getCell(index, probe.cdf_probe_information)

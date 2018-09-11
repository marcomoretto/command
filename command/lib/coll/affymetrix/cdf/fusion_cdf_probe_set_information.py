from command.lib.coll.affymetrix.affymetrix_cdf_wrapper import AffyMetrixCdfWrapper


class CdfProbeSetInformation:

    def __init__(self):
        self.affy = AffyMetrixCdfWrapper()
        self.cdf_probe_set_information = self.affy._fusionCDFProbeSetInformationAutoClass()

    def get_num_lists(self):
        return self.cdf_probe_set_information.getNumLists()

    def get_num_groups(self):
        return self.cdf_probe_set_information.getNumGroups()

    def get_num_cells(self):
        return self.cdf_probe_set_information.getNumCells()

    def get_index(self):
        return self.cdf_probe_set_information.getIndex()

    def get_probe_set_number(self):
        return self.cdf_probe_set_information.getProbeSetNumber()

    def get_probe_set_type(self):
        return self.cdf_probe_set_information.getProbeSetType()

    def get_direction(self):
        return self.cdf_probe_set_information.getDirection()

    def get_num_cells_per_list(self):
        return self.cdf_probe_set_information.getNumCellsPerList()

    def get_group(self, index, group):
        self.cdf_probe_set_information.getGroup(index, group.cdf_probe_group_information)

    def clear(self):
        self.cdf_probe_set_information.clear()

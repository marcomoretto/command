from command.lib.coll.affymetrix.affymetrix_cel_wrapper import AffyMetrixCelWrapper


class CelFileParser:

    def __init__(self):
        self.affy = AffyMetrixCelWrapper()
        self.cel = self.affy._fusionCELDataAutoClass()
        self.read_ok = False

    def open_cel_file(self, file_name):
        j_file_name = self.affy.String(file_name)
        self.set_file_name(j_file_name)
        self.read()

    ####
    # WRAPPER METHODS
    def set_file_name(self, file_name):
        self.cel.setFileName(file_name)

    def read(self, bIncludeMaskAndOutliers=None):
        if bIncludeMaskAndOutliers is None:
            self.read_ok = self.cel.read()
        self.read_ok = self.cel.read(bIncludeMaskAndOutliers != None) # Java need a bool

    def get_intensity(self, x, y=None):
        if self.cel and self.read_ok:
            if y is None:
                return self.cel.getIntensity(x)
            return self.cel.getIntensity(x, y)

    def get_error(self):
        return self.cel.getError()

    def get_file_name(self):
        return self.cel.getFileName()

    def is_multi_color(self):
        return self.cel.isMultiColor()

    def get_channels(self):
        return self.cel.getChannels()

    def set_active_datagroup(self, channel):
        return self.cel.setActiveDataGroup(channel)

    def get_cells(self):
        return self.cel.getCells()

    def index_to_x(self, n):
        return self.cel.indexToX(n)

    def index_to_y(self, n):
        return self.cel.indexToY(n)

    def xy_to_index(self, x, y):
        return self.cel.xyToIndex(x, y)

    def get_cols(self):
        return self.cel.getCols()

    def get_rows(self):
        return self.cel.getRows()

    def get_header(self):
        return self.cel.getHeader()

    def get_alg(self):
        return self.cel.getAlg()

    def get_params(self):
        return self.cel.getParams()

    def get_algorithm_parameter(self, tag):
        return self.cel.getAlgorithmParameter(tag)

    def get_algorithm_parameter_tag(self, index):
        return self.cel.getAlgorithmParameterTag(index)

    def get_number_algorithm_parameters(self):
        return self.cel.getNumberAlgorithmParameters()

    def get_algorithm_parameters(self):
        return self.cel.getAlgorithmParameters()

    def get_chip_type(self):
        return self.cel.getChipType()

    def get_master_file_name(self):
        return self.cel.getMasterFileName()

    def get_library_package_name(self):
        return self.cel.getLibraryPackageName()

    def get_dat_header(self):
        return self.cel.getDatHeader()

    def get_cell_margin(self):
        return self.cel.getCellMargin()

    def get_num_outliers(self):
        return self.cel.getNumOutliers()

    def get_num_masked(self):
        return self.cel.getNumMasked()

    def get_stdv(self, x, y=None):
        if y is None:
            return self.cel.getStdv(x)
        return self.cel.getStdv(x, y)

    def get_pixels(self, x, y=None):
        if y is None:
            return self.cel.getPixels(x)
        return self.cel.getPixels(x, y)

    def is_masked(self, x, y=None):
        if y is None:
            return self.cel.isMasked(x)
        return self.cel.isMasked(x, y)

    def is_outlier(self, x, y=None):
        if y is None:
            return self.cel.isOutlier(x)
        return self.cel.isOutlier(x, y)

    def exists(self):
        return self.cel.exists()

    def create_file_parser(self):
        self.cel.createFileParser()

    def read_header(self):
        return self.cel.readHeader()

    def clear(self):
        self.cel.clear()

    def close(self):
        self.cel.close()

    def set_active_data_group(self, group_name):
        self.cel.setActiveDataGroup(group_name)


    '''
        NOT IMPLEMENTED

        public AffymetrixGuidType getFileId()
        public GenericData getGenericData()
        public List<FusionTagValuePair> getParameters()
        public FGridCoords getGridCorners()
        public static int xyToIndex(int x, int y, int r, int c)
        public void getEntry(int index, FusionCELFileEntryType entry)
        public void getEntry(int x, int y, FusionCELFileEntryType entry)
        public List<ParameterNameValue> getDataSetParameters(String setName)


    '''

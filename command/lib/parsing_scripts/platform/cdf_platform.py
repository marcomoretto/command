import affymetrix

cdf = affymetrix.CdfFileParser()
cdf.open_cdf_file(INPUT_FILE)
cdf_probeset_inf = affymetrix.CdfProbeSetInformation()
num_of_probe_set = cdf.get_header().get_num_probe_sets()
for i_set in range(num_of_probe_set):
    probe_set = affymetrix.CdfProbeSetInformation()
    cdf.get_probe_set_information(i_set, probe_set)
    n_of_groups = probe_set.get_num_groups()
    probeset_name = cdf.get_probe_set_name(i_set)
    for i_group in range(n_of_groups):
        probe_group = affymetrix.CdfProbeGroupInformation()
        probe_set.get_group(i_group, probe_group)
        n_of_cells = probe_group.get_num_cells()
        for i_cell in range(n_of_cells):
            probe = affymetrix.CdfProbeInformation()
            probe_group.get_cell(i_cell, probe)
            #if probe.get_pbase() != probe.get_tbase(): # PM
            org_probe_id = str(probe.get_x()) + "." + str(probe.get_y())
            sequence = ''
            if probeset_name in PLATFORM_OBJECT._sequences:
                sequence = PLATFORM_OBJECT._sequences[probeset_name].get(org_probe_id, '')
            PLATFORM_OBJECT.add_bio_feature_reporter_data(
                org_probe_id,
                org_probe_id,
                sequence=sequence,
                probe_set_name=probeset_name
            )

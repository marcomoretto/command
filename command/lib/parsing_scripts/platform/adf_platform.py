def main():
    """Parse an ADF file and extract PLATFORM information

    Looks for **accession number**, **platform name**, **platform type** and **platform description**

    PARAMETERS:
        *param1* (string): The original probe id field. If it is composed by more than one field, put all of them separated with a |. For example X|Y

        *param2* (bool): If True (or 1 or a non-empty string) the probe information (sequence) will be added

    """
    import array_express as ae

    adf = ae.ADFFileParser(INPUT_FILE)
    adf.parse()

    probe_field = [x for x in PARAMETERS[0].split('|') if x != '']

    parse_data = False
    try:
        parse_data = bool(PARAMETERS[1])
    except Exception as e:
        pass

    PLATFORM_OBJECT.platform_access_id = ENTITY_NAME
    PLATFORM_OBJECT.platform_name = ','.join(adf.header['Array Design Name'])
    PLATFORM_OBJECT.description = ','.join(adf.header['Comment[Description]'])
    PLATFORM_OBJECT.platform_type = 'microarray'

    if parse_data:
        for d in adf.data:
            name = ".".join([d[k] for k in probe_field])
            PLATFORM_OBJECT.add_bio_feature_reporter_data(
                name,
                d['Reporter Name'],
                sequence=d['Reporter Sequence']
            )


if __name__ == 'builtins':
    main()
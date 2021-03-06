def main():
    """Parse a SOFT file and extract PLATFORM information

    Looks for **accession number**, **platform name**, **platform type** and **platform description**. If True is passed as parameter it will look for
    probe sequence information in the data table part of the file

    PARAMETERS:
        *param1* (bool): Read the data table information (default False)

    """
    from soft_file_parser import SoftFile

    soft = SoftFile(INPUT_FILE)
    soft.parse()

    parse_data = False
    try:
        parse_data = bool(PARAMETERS[0])
    except Exception as e:
        pass

    PLATFORM_OBJECT.platform_access_id = ENTITY_NAME
    PLATFORM_OBJECT.platform_name = soft.platforms[ENTITY_NAME].Platform_title
    PLATFORM_OBJECT.description = soft.platforms[ENTITY_NAME].Platform_description
    PLATFORM_OBJECT.platform_type = 'microarray'

    if parse_data:
        for tb in soft.platforms[ENTITY_NAME].table_data:
            if tb['ID'] == 'ID':
                continue
            PLATFORM_OBJECT.add_bio_feature_reporter_data(
                tb['ID'],
                tb['ORF'],
                probe_set_name=tb['ID'],
                sequence=tb['SEQUENCE']
            )


if __name__ == 'builtins':
    main()
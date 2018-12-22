def main():
    """Parse a CSV file containing probe sequences

    A CSV file containing probe information is parsed and probes get added to the platform.
    This script is usually used together with other PLATFORM scripts

    PARAMETERS:
        *param1* (string): The probe id field

        *param2* (string): The probe sequence


    """
    import csv

    id_field = PARAMETERS[0]
    seq_field = PARAMETERS[1]

    with open(INPUT_FILE) as f:
        rdr = csv.DictReader(row for row in f if not row.startswith('#'))
        for row in rdr:
            PLATFORM_OBJECT.add_bio_feature_reporter_data(
                row[id_field],
                row[id_field],
                sequence=row[seq_field]
            )


if __name__ == 'builtins':
    main()
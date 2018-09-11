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
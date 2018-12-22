def main():
    """Parse a GPR file and extract SAMPLE raw data

    A GPR file is a TAB-delimited file with headers and complete sample raw data information

    PARAMETERS:
        *param1* (string): The column header of the original probe id to parse out. If it is composed by more than one field, put all of them separated with a |. For example X|Y (actual probe ids will be concatenated with dots . in that case)

        *param2* (string): The column header of the data value you want to parse out

        *param3* (int): Number of lines to skip

        *param4* (int): The sample channel (optional)

    """


    from column_identifier import sample_column_identifier
    import itertools

    # Get info from passed input
    #   SCRIPT_PARAMETERS[0] - the column header(s) of the probe identifiers you want to parse out; if multiple seperate with a pipe | (actual probe ids will be concatenated with dots . in that case)
    #   SCRIPT_PARAMETERS[1] - the column header of the data you want to parse out
    #   SCRIPT_PARAMETERS[2] - the number of header lines to skip (optional)
    #   SCRIPT_PARAMETERS[3] - the database field to match with probe_id (optional; default is org_probe_id)
    #   SCRIPT_PARAMETERS[4] - temporary override for original platform in case structuring assignments don't stick


    probe_field = [x for x in PARAMETERS[0].split('|') if x != '']
    value_field = PARAMETERS[1] if len(PARAMETERS) > 1 else None
    line_skip = int(PARAMETERS[2]) if len(PARAMETERS) > 2 else 0
    SAMPLE_OBJECT.channel_label = PARAMETERS[3] if len(
        PARAMETERS) > 3 else SAMPLE_OBJECT.channel_label if SAMPLE_OBJECT.channel_label else None
    header = []
    with open(INPUT_FILE, encoding="utf8", errors='ignore') as f:
        for line in itertools.islice(f, line_skip, None):
            if len(header) == 0:
                header = [x.strip() for x in line.replace('"', '').split('\t')]
                if not value_field:
                    identified_field = sample_column_identifier(SAMPLE_OBJECT.channel_label, header)
                    if not identified_field:
                        print(
                            '<b>' + ENTITY_NAME + '</b>: no columns identified for channel label <b>' + SAMPLE_OBJECT.channel_label + '</b>')
                        break
                    elif len(identified_field) > 1:
                        print('<b>' + ENTITY_NAME + '</b>:', os.path.basename(
                            INPUT_FILENAME) + ' multiple columns identified for channel label <b>' + SAMPLE_OBJECT.channel_label + '</b>:')
                        print(identified_field)
                        break
                    else:
                        value_field = identified_field[0]
                try:
                    probe_ind = [header.index(pf) for pf in probe_field]
                except Exception as e:
                    print('<b>' + ENTITY_NAME + '</b>: probe id field(s) not found')
                    break
                try:
                    value_ind = header.index(value_field)
                except Exception as e:
                    print('<b>' + ENTITY_NAME + '</b>: value field not found')
                    break
                continue
            row = [x.strip() for x in line.split('\t')]
            try:
                name = '.'.join([row[pi].replace('"', '') for pi in probe_ind])
                if 'corner' in name.lower():
                    continue
                SAMPLE_OBJECT.add_raw_data(name, row[value_ind].replace('"', ''))
            except Exception as e:
                print('<b>' + ENTITY_NAME + '</b>: ignored line "' + line.strip() + '"')


if __name__ == 'builtins':
    main()
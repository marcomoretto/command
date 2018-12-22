def main():
    """Parse a CEL (Affymetrix) file and extract SAMPLE raw data

    The probe original id is given by X.Y

    PARAMETERS:
        None

    """


    import affymetrix

    cel = affymetrix.CelFileParser()
    cel.open_cel_file(INPUT_FILE)
    for i in range(cel.get_cells()):
        x = str(cel.index_to_x(i))
        y = str(cel.index_to_y(i))
        val = cel.get_intensity(i)
        SAMPLE_OBJECT.add_raw_data(x + '.' + y, val)


if __name__ == 'builtins':
    main()
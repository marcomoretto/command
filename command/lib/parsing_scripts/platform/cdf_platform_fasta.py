def main():
    """Parse a FASTA file containing probe sequences

    This script is usually used before cdf_platform.py in order to get the probe sequence information that a CDF file doesn't provide.

    PARAMETERS:
        None

    """
    import affymetrix
    import os

    PLATFORM_OBJECT._sequences = {}
    # example >probe:HG-U133_Plus_2:1007_s_at:718:317; Interrogation_Position=3330; Antisense;
    with open(INPUT_FILE) as f:
        for l in f:
            if l.startswith('>'):
                id_l = l.strip()[1:].split(';')[0].split(':')
                probeset = id_l[2]
                xy = str(id_l[3]) + "." + str(id_l[4])
                if probeset not in PLATFORM_OBJECT._sequences:
                    PLATFORM_OBJECT._sequences[probeset] = {}
                if xy not in PLATFORM_OBJECT._sequences[probeset]:
                    PLATFORM_OBJECT._sequences[probeset][xy] = ''
            else:
                PLATFORM_OBJECT._sequences[probeset][xy] += l.strip()


if __name__ == 'builtins':
    main()

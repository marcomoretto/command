def main():
    """Trim a FASTQ file using Trimmomatic and quantify using KALLISTO

    The result counts will be added to the SAMPLE OBJECT

    PARAMETERS:
        *param1* (bool): True if this FASTQ file has a PAIRED file (forward or reverse), default False

    """


    import rnaseq
    import os

    paired = PARAMETERS[0] if len(PARAMETERS) > 0 else None
    dir_name = os.path.dirname(INPUT_FILE)
    trim = rnaseq.Trimmomatic(INPUT_FILE.split('_')[0], paired)
    out_trim, err_trim = trim.run()
    kallisto = rnaseq.Kallisto()
    out_kal, err_kal, out_file = kallisto.quantify(COMPENDIUM, trim.ofp, trim.orp)
    with open(out_file) as f:
        next(f)
        for l in f:
            s = l.strip().split('\t')
            SAMPLE_OBJECT.add_raw_data(s[0], s[3])


if __name__ == 'builtins':
    main()
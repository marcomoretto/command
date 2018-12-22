def main():
    """Create an index file for the KALLISTO software using the current BIOLOGICAL FEATURES

    Biologial features for this compendium are putted into a FASTA file that is then indexed
    to be used for RNA-seq quantification using KALLISTO

    PARAMETERS:
        None

    """
    import rnaseq

    rnaseq.create_fasta(INPUT_FILE, COMPENDIUM)
    kallisto = rnaseq.Kallisto()
    out, err = kallisto.build_index(INPUT_FILE, COMPENDIUM)


if __name__ == 'builtins':
    main()
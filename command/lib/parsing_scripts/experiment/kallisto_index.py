import rnaseq

rnaseq.create_fasta(INPUT_FILE, COMPENDIUM)
kallisto = rnaseq.Kallisto()
out, err = kallisto.build_index(INPUT_FILE, COMPENDIUM)
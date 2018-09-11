import os
import subprocess
from command.lib.db.compendium.bio_feature import BioFeature
from cport import settings


class Kallisto:
    def __init__(self):
        pass

    def build_index(self, fasta_file, index_name):
        path = os.path.dirname(fasta_file)
        cmd = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'kallisto')
        cmd += '/kallisto index --index=' + os.path.join(path, index_name) + ' ' + fasta_file
        process = subprocess.Popen(cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
        (out, err) = process.communicate()
        return str(out), str(err)

    def quantify(self, index_name, forward, reverse=None):
        path = os.path.dirname(forward)
        basename = index_name + '_' + os.path.basename(forward).split('_')[0]
        out_dir = os.path.join(path, basename)
        out_file = os.path.join(path, basename + '.tsv')
        cmd = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'kallisto')
        if reverse:
            cmd += '/kallisto quant --index=' + os.path.join(path, index_name) + \
                ' --threads=1 --plaintext --output-dir=' + out_dir + ' ' + forward + ' ' + reverse
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       shell=True)
            (out, err) = process.communicate()
            os.rename(os.path.join(out_dir, 'abundance.tsv'), out_file)
            return str(out), str(err), out_file


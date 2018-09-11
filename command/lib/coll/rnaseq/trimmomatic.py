import os
import subprocess
from cport import settings


class Trimmomatic:

    def __init__(self, file_basename,
                 paired,
                 pe='phred33',
                 clip='TruSeq3-PE.fa:2:30:10',
                 leading=1,
                 trailing=1,
                 sli_win='4:15',
                 minlen='20',
                 ):
        adapter_dir = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'trimmomatic', 'adapters')
        self.cmd = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'trimmomatic')
        self.cmd += '/trimmomatic-0.38.jar '
        if paired:
            self.iff = file_basename + "_1.fastq"
            self.irf = file_basename + "_2.fastq"
            self.ofp = file_basename + "_out_fp.fastq"
            self.ofu = file_basename + "_out_fu.fastq"
            self.orp = file_basename + "_out_rp.fastq"
            self.oru = file_basename + "_out_ru.fastq"
            self.cmd += 'PE -' + str(pe) + ' -threads 1 '
            self.cmd += ' '.join([self.iff, self.irf, self.ofp, self.ofu, self.orp, self.oru]) + ' '
            self.cmd += 'ILLUMINACLIP:' + adapter_dir + '/' + clip + ' '
            self.cmd += 'LEADING:' + str(leading) + ' '
            self.cmd += 'TRAILING:' + str(trailing) + ' '
            self.cmd += 'SLIDINGWINDOW:' + str(sli_win) + ' '
            self.cmd += 'MINLEN:' + str(minlen)
        else:
            pass
        self.cmd = 'java -jar ' + self.cmd

    def run(self):
        process = subprocess.Popen(self.cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True)
        (out, err) = process.communicate()
        return str(out), str(err)
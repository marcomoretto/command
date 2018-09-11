import json
import os
import subprocess
from ftplib import FTP
from os.path import isfile, join
from urllib.parse import urlparse
from urllib.request import urlretrieve

from Bio import Entrez
import requests
from django.db import transaction

from command.lib.coll.array_express.sdrf_file_parser import SDRFFileParser
from command.lib.coll.experiment_data_collection_manager import ExperimentDataCollectionManager
from command.lib.coll.soft_file_parser import SoftFile
from command.lib.db.admin.admin_options import AdminOptions
from command.lib.db.admin.compendium_database import CompendiumDatabase
from command.lib.db.compendium.bio_feature import BioFeature
from command.lib.db.compendium.bio_feature_reporter import BioFeatureReporter
from command.lib.db.compendium.experiment import Experiment
from command.lib.db.compendium.experiment_search_result import ExperimentSearchResult
from command.lib.db.compendium.platform_type import PlatformType
from command.lib.db.compendium.status import Status
from command.lib.db.compendium.platform import Platform
from command.lib.db.compendium.sample import Sample
from command.lib.utils import file_system
from xml.dom.minidom import parse, parseString

from cport import settings
import datetime

class PublicDatabase(ExperimentDataCollectionManager):

    def __init__(self):
        ExperimentDataCollectionManager.__init__(self)

    def search(self, term, email, db_id, abortable_fun=lambda: False):
        raise NotImplementedError()

    def download_experiment_files(self, experiment_accession, email, out_dir):
        raise NotImplementedError()

    @property
    def experiment_accession_base_link(self):
        return ""

    @property
    def platform_accession_base_link(self):
        return ""

    @property
    def scientific_paper_accession_base_link(self):
        return ""


class SRAPublicDatabase(PublicDatabase):
    EXPERIMENT_ACCESSION_BASE_LINK = 'https://www.ncbi.nlm.nih.gov/bioproject/'
    PLATFORM_ACCESSION_BASE_LINK = None
    SCIENTIFIC_PAPER_BASE_LINK = 'https://www.ncbi.nlm.nih.gov/pubmed/?term='

    def __init__(self):
        ExperimentDataCollectionManager.__init__(self)

    def search(self, term, email, db_id, abortable_fun=lambda: False):
        Entrez.email = email  # Always tell NCBI who you are
        t = term + ' AND ("transcriptome gene expression"[Filter] AND "bioproject sra"[Filter])'
        handle = Entrez.esearch(db="bioproject",
                                term=t,
                                retmode='xml',
                                retmax=100000000)
        results = Entrez.read(handle)
        r = {}
        sorted_id = sorted(results['IdList'], key=lambda k: int(k), reverse=True)

        if not sorted_id:
            handle = Entrez.esearch(db="bioproject",
                                    term=term,
                                    retmode='xml',
                                    retmax=100000000)
            results = Entrez.read(handle)
            r = {}
            sorted_id = sorted(results['IdList'], key=lambda k: int(k), reverse=True)
            if not sorted_id:
                return []

        link = Entrez.elink(
            db='gds',
            dbfrom='bioproject',
            retmode='xml',
            id=','.join(sorted_id)
        )
        result_link = Entrez.read(link)
        gds_ids = []
        if result_link[0]['LinkSetDb']:
            gds_ids = [e['Id'] for e in result_link[0]['LinkSetDb'][0]['Link']]
        link_map = dict(zip(gds_ids, result_link[0]['IdList']))
        exp_map = {}
        if sorted_id:
            handle_summary_bp = Entrez.esummary(db="bioproject", id=",".join(sorted_id))
            results_summary_bp = Entrez.read(handle_summary_bp)
            for bp_summary in results_summary_bp['DocumentSummarySet']['DocumentSummary']:
                if abortable_fun():
                    break
                exp_result = ExperimentSearchResult()
                exp_result.ori_result_id = bp_summary['Project_Id']
                exp_result.date = datetime.datetime.strptime(
                    bp_summary['Registration_Date'],
                    '%Y/%m/%d %H:%M'
                ).strftime('%Y-%m-%d')
                exp_result.data_source_id = db_id
                exp_result.experiment_access_id = bp_summary['Project_Acc']
                exp_result.experiment_name = bp_summary['Project_Title']
                exp_result.organism = bp_summary['Organism_Label'] + ' ' + \
                                      bp_summary['Organism_Name'] + ' ' + \
                                      bp_summary['Organism_Strain']
                exp_result.type = bp_summary['Project_Data_Type']
                exp_result.description = bp_summary['Project_Description']
                exp_map[exp_result.experiment_access_id] = exp_result.ori_result_id
                r[exp_result.ori_result_id] = exp_result
            handle_summary_bp.close()

            samples = self._get_platform_samples_summary([e.ori_result_id for i, e in r.items()], email)
            for exp_id, rest in samples.items():
                if exp_id not in exp_map or exp_map[exp_id] not in r:
                    continue
                r[exp_map[exp_id]].platform = ';'.join(list(rest.keys()))
                r[exp_map[exp_id]].n_samples = len(list(rest.values())[0])

        if gds_ids:
            handle_summary_gds = Entrez.esummary(db="gds", id=",".join(gds_ids))
            result_summary_gds = Entrez.read(handle_summary_gds)
            for geo_summary in result_summary_gds:
                if abortable_fun():
                    break
                if geo_summary['Accession'].startswith('GSE'):
                    exp_result = r[link_map[geo_summary['Id']]]
                    pubmed = ''
                    if len(geo_summary['PubMedIds']) > 0:
                        pubmed = geo_summary['PubMedIds'][0]

                    exp_result.experiment_alternative_access_id = geo_summary['Accession']
                    exp_result.scientific_paper_ref = pubmed
            handle_summary_gds.close()

        handle.close()
        link.close()

        return list(r.values())

    def create_experiment_structure(self, compendium_id, experiment_id, out_dir):
        log = ''
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        data_ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_data_ready')

        searched_exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=experiment_id)

        exp_samples = self._get_platform_samples([searched_exp.ori_result_id], '@')

        new_platforms = {}
        for exp_id, rest in exp_samples.items():
            for plt_id, samples in rest.items():
                platform = Platform()
                try:
                    platform = Platform.objects.using(compendium.compendium_nick_name). \
                        get(platform_access_id=plt_id)
                except Exception as e:
                    platform.platform_access_id = plt_id
                    platform.platform_name = plt_id
                    platform.description = plt_id
                    platform.data_source = searched_exp.data_source
                    platform.platform_type = PlatformType.objects.\
                        using(compendium.compendium_nick_name).get(name='rnaseq')
                new_platforms[platform.platform_access_id] = platform

        with transaction.atomic(using=compendium.compendium_nick_name):
            all_samples = Sample.objects.using(compendium.compendium_nick_name). \
                values_list('sample_name', flat=True)
            new_exp = Experiment()
            new_exp.organism = searched_exp.organism
            new_exp.experiment_access_id = searched_exp.experiment_access_id
            new_exp.experiment_name = searched_exp.experiment_name
            new_exp.scientific_paper_ref = searched_exp.scientific_paper_ref
            new_exp.description = searched_exp.description
            new_exp.status = data_ready_status
            new_exp.data_source = searched_exp.data_source
            new_exp.save(using=compendium.compendium_nick_name)
            samples = []
            for pl_id, pl in new_platforms.items():
                pl.save(using=compendium.compendium_nick_name)
                count = 0
                try:
                    count = pl.biofeaturereporter_set.count()
                except Exception as e:
                    pass
                if count == 0:
                    rna_seq_reporters = []
                    for gid, gname in BioFeature.objects.using(compendium.compendium_nick_name).values_list('id', 'name'):
                        rep = BioFeatureReporter()
                        rep.name = gname
                        rep.description = gname
                        rep.platform_id = pl.id
                        rep.bio_feature_id = gid
                        rna_seq_reporters.append(rep)
                    BioFeatureReporter.objects.using(compendium.compendium_nick_name).bulk_create(rna_seq_reporters)
            for exp_id, rest in exp_samples.items():
                for plt_id, smps in rest.items():
                    for smp in smps:
                        sample = Sample()
                        sample.sample_name = smp[0]
                        if sample.sample_name in all_samples:
                            log += "Duplicated sample " + sample.sample_name + "<br>"
                            continue
                        sample.description = smp[1]
                        sample.experiment = new_exp
                        sample.platform = new_platforms[plt_id]
                        sample.reporter_platform = new_platforms[plt_id]
                        samples.append(sample)
            Sample.objects.using(compendium.compendium_nick_name).bulk_create(samples)
        # create genes fasta file
        base_output_directory = AdminOptions.objects.get(option_name='download_directory')
        out_dir = os.path.join(base_output_directory.option_value,
                               compendium.compendium_nick_name,
                               searched_exp.experiment_access_id)
        gene_file_name = os.path.join(out_dir, compendium.compendium_nick_name + '.fasta')
        with open(gene_file_name, 'w') as f:
            for gene in BioFeature.objects.using(compendium.compendium_nick_name).all():
                try:
                    sequence = gene.biofeaturevalues_set.filter(bio_feature_field__name='sequence')[0].value
                    f.write('>' + str(gene.name) + '\n' + str(sequence) + '\n')
                except Exception as e:
                    pass
        return log

    def download_experiment_files(self, experiment_accession, email, out_dir):
        Entrez.email = email  # Always tell NCBI who you are
        handle = Entrez.esearch(db="bioproject",
                                term=experiment_accession,
                                retmode='xml',
                                retmax=100000000)
        results = Entrez.read(handle)
        sorted_id = sorted(results['IdList'], key=lambda k: int(k), reverse=True)
        samples = self._get_platform_samples(sorted_id, email)
        for exp_id, rest in samples.items():
            for plt_id, samples in rest.items():
                for sample in samples:
                    cmd = os.path.join(settings.BASE_DIR, 'command', 'external_programs', 'sra-toolkit', 'bin')
                    cmd += '/fastq-dump -I --split-files -O ' + out_dir + ' ' + sample[0]
                    process = subprocess.Popen(cmd,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 shell=True)
                    (out, err) = process.communicate()

    def _get_platform_samples_summary(self, experiment_ids, email):
        samples = {}
        Entrez.email = email  # Always tell NCBI who you are
        link = Entrez.elink(
            db='sra',
            dbfrom='bioproject',
            retmode='xml',
            id=','.join(experiment_ids)
        )
        result_link = Entrez.read(link)
        sample_ids = [e['Id'] for e in result_link[0]['LinkSetDb'][0]['Link']]

        handle_summary = Entrez.esummary(db="sra", id=','.join(sample_ids), retmode='xml', retmax=100000000)
        xml = parseString(handle_summary.read())
        for doc in xml.getElementsByTagName('DocSum'):
            markup = doc.getElementsByTagName('Item')[0].firstChild.data
            id = doc.getElementsByTagName('Id')[0].firstChild.data
            bp_start = '<Bioproject>'
            bp_end = '</Bioproject>'
            bp_start_ix = markup.find(bp_start) + len(bp_start)
            bp_end_ix = markup.find(bp_end)
            bp = markup[bp_start_ix:bp_end_ix]
            pl_start = '<Platform instrument_model="'
            pl_end = '">'
            pl_start_ix = markup.find(pl_start) + len(pl_start)
            pl_end_ix = markup.find(pl_end, pl_start_ix)
            pl = markup[pl_start_ix:pl_end_ix]
            if bp not in samples:
                samples[bp] = {}
            if pl not in samples[bp]:
                samples[bp][pl] = []
            samples[bp][pl].append(id)
        return samples

    def _get_platform_samples(self, experiment_ids, email):
        samples = {}
        Entrez.email = email  # Always tell NCBI who you are
        link = Entrez.elink(
            db='sra',
            dbfrom='bioproject',
            retmode='xml',
            id=','.join(experiment_ids)
        )
        result_link = Entrez.read(link)
        sample_ids = [e['Id'] for e in result_link[0]['LinkSetDb'][0]['Link']]

        handle_summary = Entrez.efetch(db="sra", id=','.join(sample_ids), retmode='xml', retmax=100000000)
        xml = parseString(handle_summary.read())
        for e in xml.getElementsByTagName('EXPERIMENT_PACKAGE'):
            for db in e.getElementsByTagName('XREF_LINK'):
                if db.getElementsByTagName('DB')[0].firstChild.data.lower() == 'bioproject':
                    exp_id = db.getElementsByTagName('ID')[0].firstChild.data
                    platform = e.getElementsByTagName('INSTRUMENT_MODEL')[0].firstChild.data
                    srr = e.getElementsByTagName('RUN_SET')[0].firstChild.attributes['accession'].value
                    gsm = None
                    sample_description = None
                    if 'refname' in e.getElementsByTagName('RUN_SET')[0].firstChild.getElementsByTagName('EXPERIMENT_REF')[0].attributes:
                        gsm = e.getElementsByTagName('RUN_SET')[0].firstChild. \
                            getElementsByTagName('EXPERIMENT_REF')[0].attributes['refname'].value
                    if len(e.getElementsByTagName('LIBRARY_CONSTRUCTION_PROTOCOL')) > 0:
                        sample_description = e.getElementsByTagName('LIBRARY_CONSTRUCTION_PROTOCOL')[0].firstChild.data
                    if exp_id not in samples:
                        samples[exp_id] = {}
                    if platform not in samples[exp_id]:
                        samples[exp_id][platform] = []
                    samples[exp_id][platform].append((srr, sample_description, gsm))
        return samples

    @property
    def scientific_paper_accession_base_link(self):
        return SRAPublicDatabase.SCIENTIFIC_PAPER_BASE_LINK

    @property
    def platform_accession_base_link(self):
        return SRAPublicDatabase.PLATFORM_ACCESSION_BASE_LINK

    @property
    def experiment_accession_base_link(self):
        return SRAPublicDatabase.EXPERIMENT_ACCESSION_BASE_LINK


class ArrayExpressPublicDatabase(PublicDatabase):
    EXPERIMENT_ACCESSION_BASE_LINK = "https://www.ebi.ac.uk/arrayexpress/experiments/"
    PLATFORM_ACCESSION_BASE_LINK = "https://www.ebi.ac.uk/arrayexpress/arrays/"
    SCIENTIFIC_PAPER_BASE_LINK = "http://europepmc.org/abstract/MED/"

    def __init__(self):
        self.ae_search_url = 'https://www.ebi.ac.uk/arrayexpress/json/v3/experiments?'
        self.ae_file_url = 'https://www.ebi.ac.uk/arrayexpress/json/v3/files?'
        super(ArrayExpressPublicDatabase, self).__init__()


    @property
    def scientific_paper_accession_base_link(self):
        return ArrayExpressPublicDatabase.SCIENTIFIC_PAPER_BASE_LINK

    @property
    def platform_accession_base_link(self):
        return ArrayExpressPublicDatabase.PLATFORM_ACCESSION_BASE_LINK

    @property
    def experiment_accession_base_link(self):
        return ArrayExpressPublicDatabase.EXPERIMENT_ACCESSION_BASE_LINK

    def create_experiment_structure(self, compendium_id, experiment_id, out_dir):
        log = ''
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        data_ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_data_ready')

        searched_exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=experiment_id)

        onlyfiles = [f for f in os.listdir(out_dir) if isfile(join(out_dir, f)) and
                     '.sdrf' in f.lower()]
        if len(onlyfiles) == 0:
            return

        sdrf = SDRFFileParser(join(out_dir, onlyfiles[0]))
        sdrf.parse()

        new_platforms = {}
        for plt in sdrf.get_platforms():
            platform = Platform()
            try:
                platform = Platform.objects.using(compendium.compendium_nick_name). \
                    get(platform_access_id=plt)
            except Exception as e:
                platform.platform_access_id = plt
                platform.platform_name = plt
                platform.description = plt
                platform.data_source = searched_exp.data_source
            new_platforms[platform.platform_access_id] = platform

        with transaction.atomic(using=compendium.compendium_nick_name):
            all_samples = Sample.objects.using(compendium.compendium_nick_name). \
                values_list('sample_name', flat=True)
            new_exp = Experiment()
            new_exp.organism = searched_exp.organism
            new_exp.experiment_access_id = searched_exp.experiment_access_id
            new_exp.experiment_name = searched_exp.experiment_name
            new_exp.scientific_paper_ref = searched_exp.scientific_paper_ref
            new_exp.description = searched_exp.description
            new_exp.status = data_ready_status
            new_exp.data_source = searched_exp.data_source
            new_exp.save(using=compendium.compendium_nick_name)
            samples = []
            for pl_id, pl in new_platforms.items():
                pl.save(using=compendium.compendium_nick_name)
                for smp in sdrf.get_samples(pl_id):
                    sample_channels = int(sdrf.get_number_of_channel(smp))
                    for ch in range(1, sample_channels + 1):
                        sample = Sample()
                        sample.sample_name = smp + '.ch' + str(ch)
                        if sample.sample_name in all_samples:
                            log += "Duplicated sample " + sample.sample_name + "<br>"
                            continue
                        sample.description = smp
                        sample.experiment = new_exp
                        sample.platform = pl
                        sample.reporter_platform = pl
                        samples.append(sample)

            Sample.objects.using(compendium.compendium_nick_name).bulk_create(samples)
        return log

    def download_experiment_files(self, experiment_accession, email, out_dir):
        resp = requests.get(self.ae_file_url + "accession=" + experiment_accession)
        j = json.loads(resp.text)
        for f in j['files']['experiment']['file']:
            output = os.path.join(out_dir, f['name'])
            urlretrieve(f['url'], output)
            if f['extension'] == 'zip':
                file_system.extract_zipfile(output, out_dir)
                os.remove(output)
            if f['extension'] == 'gz':
                output_uncompressed, file_extension = os.path.splitext(output)
                file_system.extract_gzfile(output, output_uncompressed)
                os.remove(output)

    def search(self, term, email, db_id, abortable_fun=lambda: False):
        resp = requests.get(self.ae_search_url + 'keywords=' + term)
        j = json.loads(resp.text)
        r = []
        for exp in j['experiments']['experiment']:
            platform = []
            samples = []
            pubmed = ''
            ty = ''
            accession = exp['accession']
            alternative_accession = ''
            if 'secondaryaccession' in exp:
                if isinstance(exp['secondaryaccession'], list):
                    for acc in exp['secondaryaccession']:
                        alternative_accession = acc
                        break
                else:
                    alternative_accession = exp['secondaryaccession']
            if 'arraydesign' in exp:
                if isinstance(exp['arraydesign'], list):
                    for design in exp['arraydesign']:
                        if design and 'accession' in design:
                            platform.append(design['accession'])
                        if design and 'count' in design:
                            samples.append(int(design['count']))
            if 'bibliography' in exp:
                if isinstance(exp['bibliography'], list):
                 for bib in exp['bibliography']:
                     if bib and 'accession' in bib:
                        pubmed = str(bib['accession'])
            if 'experimenttype' in exp:
                ty = exp['experimenttype']
                if isinstance(ty, list):
                    ty = ','.join(ty)
            exp_result = ExperimentSearchResult()
            exp_result.ori_result_id = int(exp['id'])
            exp_result.date = exp['releasedate']
            exp_result.data_source_id = db_id
            exp_result.experiment_name = exp['name'].encode('ascii', 'ignore')
            exp_result.organism = exp['organism']
            if isinstance(exp['organism'], list):
                exp_result.organism = ','.join(exp['organism'])
            exp_result.experiment_access_id = accession.encode('ascii', 'ignore')
            exp_result.experiment_alternative_access_id = alternative_accession.encode('ascii', 'ignore')
            exp_result.n_samples = sum(samples)
            exp_result.type = ty
            exp_result.platform = ','.join(platform)
            exp_result.scientific_paper_ref = pubmed.encode('ascii', 'ignore')
            if isinstance(exp['description'], list):
                for desc in exp['description']:
                    if isinstance(desc['text'], str):
                        exp_result.description = desc['text'].encode('ascii', 'ignore')
                        break
            r.append(exp_result)
        return r


class GEOPublicDatabase(PublicDatabase):

    EXPERIMENT_ACCESSION_BASE_LINK = 'http://130.14.29.110/geo/query/acc.cgi?acc='
    PLATFORM_ACCESSION_BASE_LINK = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc='
    SCIENTIFIC_PAPER_BASE_LINK = 'https://www.ncbi.nlm.nih.gov/pubmed/?term='

    def __init__(self):
        self.ncbi_geo_base_ftp = 'ftp.ncbi.nih.gov'
        self.ncbi_geo_soft_series_base_dir = '/pub/geo/DATA/SOFT/by_series/'
        self.ncbi_geo_soft_platform_base_dir = '/pub/geo/DATA/SOFT/by_platform/'
        super(GEOPublicDatabase, self).__init__()
        self._word = 'word'

    @property
    def scientific_paper_accession_base_link(self):
        return GEOPublicDatabase.SCIENTIFIC_PAPER_BASE_LINK

    @property
    def platform_accession_base_link(self):
        return GEOPublicDatabase.PLATFORM_ACCESSION_BASE_LINK

    @property
    def experiment_accession_base_link(self):
        return GEOPublicDatabase.EXPERIMENT_ACCESSION_BASE_LINK

    def download_experiment_files(self, experiment_accession, email, out_dir):
        ftp_site, ftp_dir = self._get_experiment_ftp_details_by_id(experiment_accession, email)
        ftp = FTP(ftp_site)
        ftp.login()
        ftp.cwd(ftp_dir)
        files = ftp.nlst()
        for f in files:
            full_file_path = os.path.join(ftp_dir, f)
            output = os.path.join(out_dir, f)
            ftp.retrbinary('RETR ' + full_file_path, open(output, 'wb').write)
            output_uncompressed, file_extension = os.path.splitext(output)
            file_system.extract_gzfile(output, output_uncompressed)
            os.remove(output)
        ftp.close()
        self._download_supplementary_files(out_dir)

    def search(self, term, email, db_id, abortable_fun=lambda: False):
        Entrez.email = email  # Always tell NCBI who you are
        handle = Entrez.esearch(db="gds", term=term, retmax=100000000)
        results = Entrez.read(handle)
        r = []
        sorted_id = sorted(results['IdList'], key=lambda k: int(k), reverse=True)

        handle_summary = Entrez.esummary(db="gds", id=",".join(sorted_id))
        results_summary = Entrez.read(handle_summary)
        for geo_summary in results_summary:
            if abortable_fun():
                break
            if geo_summary['Accession'].startswith('GSE'):
                pubmed = ''
                if len(geo_summary['PubMedIds']) > 0:
                    pubmed = geo_summary['PubMedIds'][0]

                exp_result = ExperimentSearchResult()
                exp_result.ori_result_id = geo_summary['Id']
                exp_result.date = datetime.datetime.strptime(
                    geo_summary['PDAT'],
                    '%Y/%m/%d'
                ).strftime('%Y-%m-%d')
                exp_result.data_source_id = db_id
                exp_result.experiment_access_id = geo_summary['Accession']
                exp_result.n_samples = geo_summary['n_samples']
                exp_result.experiment_name = geo_summary['title']
                exp_result.organism = geo_summary['taxon']
                exp_result.type = geo_summary['gdsType']
                exp_result.platform = ";".join(['GPL' + plt for plt in geo_summary['GPL'].split(';')])
                exp_result.scientific_paper_ref = pubmed
                exp_result.description = geo_summary['summary']
                r.append(exp_result)

        handle_summary.close()
        handle.close()

        return r

    def create_experiment_structure(self, compendium_id, experiment_id, out_dir):
        log = ''
        compendium = CompendiumDatabase.objects.get(id=compendium_id)
        data_ready_status = Status.objects.using(compendium.compendium_nick_name).get(name='experiment_data_ready')

        searched_exp = ExperimentSearchResult.objects.using(compendium.compendium_nick_name).get(id=experiment_id)

        onlyfiles = [f for f in os.listdir(out_dir) if isfile(join(out_dir, f)) and
                     f.lower().startswith('gse') and f.lower().endswith('soft')]
        if len(onlyfiles) == 0:
            return
        soft = SoftFile(join(out_dir, onlyfiles[0]))
        soft.parse()

        new_platforms = {}
        for id, plt in soft.platforms.items():
            platform = Platform()
            try:
                platform = Platform.objects.using(compendium.compendium_nick_name).\
                    get(platform_access_id=plt.Platform_geo_accession)
            except Exception as e:
                platform.platform_access_id = plt.Platform_geo_accession
                platform.platform_name = plt.Platform_title
                platform.description = plt.Platform_description if hasattr(plt, 'Platform_description') else None
                platform.data_source = searched_exp.data_source
            new_platforms[platform.platform_access_id] = platform

        with transaction.atomic(using=compendium.compendium_nick_name):
            all_samples = Sample.objects.using(compendium.compendium_nick_name).\
                values_list('sample_name', flat=True)
            new_exp = Experiment()
            new_exp.organism = searched_exp.organism
            new_exp.experiment_access_id = searched_exp.experiment_access_id
            new_exp.experiment_name = searched_exp.experiment_name
            new_exp.scientific_paper_ref = searched_exp.scientific_paper_ref
            new_exp.description = searched_exp.description
            new_exp.status = data_ready_status
            new_exp.data_source = searched_exp.data_source
            new_exp.save(using=compendium.compendium_nick_name)
            samples = []
            for pl_id, pl in new_platforms.items():
                pl.save(using=compendium.compendium_nick_name)
            for id, smp in soft.samples.items():
                sample_channels = int(smp.Sample_channel_count)
                for ch in range(1, sample_channels + 1):
                    sample = Sample()
                    sample.sample_name = smp.Sample_geo_accession.replace('.', '_') + '.ch' + str(ch)
                    if sample.sample_name in all_samples:
                        log += "Duplicated sample " + sample.sample_name + "<br>"
                        continue
                    sample.description = smp.Sample_description if hasattr(smp, 'Sample_description') else None
                    sample.experiment = new_exp
                    sample.platform = new_platforms[smp.Sample_platform_id]
                    sample.reporter_platform = new_platforms[smp.Sample_platform_id]
                    samples.append(sample)

            Sample.objects.using(compendium.compendium_nick_name).bulk_create(samples)
        return log

    def _download_supplementary_files(self, out_dir):
        onlyfiles = [f for f in os.listdir(out_dir) if isfile(join(out_dir, f)) and
                     f.lower().startswith('gse') and f.lower().endswith('soft')]
        if len(onlyfiles) == 0:
            return

        soft = SoftFile(join(out_dir, onlyfiles[0]))
        soft.parse()

        supplementary_files = []
        for k, v in soft.series.items():
            try:
                if isinstance(v.Series_supplementary_file, list):
                    supplementary_files.extend(v.Series_supplementary_file)
                else:
                    supplementary_files.append(v.Series_supplementary_file)
            except AttributeError as e:
                pass
        for k, v in soft.platforms.items():
            try:
                if isinstance(v.Platform_supplementary_file, list):
                    supplementary_files.extend(v.Platform_supplementary_file)
                else:
                    supplementary_files.append(v.Platform_supplementary_file)
            except AttributeError as e:
                pass
        for k, v in soft.samples.items():
            try:
                if isinstance(v.Sample_supplementary_file, list):
                    supplementary_files.extend(v.Sample_supplementary_file)
                else:
                    supplementary_files.append(v.Sample_supplementary_file)
            except AttributeError as e:
                pass
        ftp = FTP(self.ncbi_geo_base_ftp)
        ftp.login()
        for file in supplementary_files:
            url = urlparse(file)
            ftp_file_name = url.path
            file_name = os.path.basename(file)
            output = os.path.join(out_dir, file_name)
            try:
                ftp.retrbinary('RETR ' + ftp_file_name, open(output, 'wb').write)
            except Exception as e:
                pass
            output_uncompressed, file_extension = os.path.splitext(output)
            try:
                file_system.extract_gzfile(output, output_uncompressed)
            except Exception as e:
                pass
            try:
                file_system.extract_tarfile(output)
            except Exception as e:
                pass
            os.remove(output)
        ftp.close()

    def _get_experiment_ftp_details_by_id(self, term, email):
        # first check if the file exist in the base FTP directory
        ftp_url = self.ncbi_geo_base_ftp
        ftp_path = os.path.join(self.ncbi_geo_soft_series_base_dir, term)
        ftp = FTP(ftp_url)
        ftp.login()
        try:
            ftp.cwd(ftp_path)
        except Exception as e:
            Entrez.email = email # Always tell NCBI who you are
            handle = Entrez.esearch(db="gds", term=term, retmax=1)
            results = Entrez.read(handle)
            ftp = ""
            for geo_id in results['IdList']:
                handle_summary = Entrez.esummary(db="gds", id=geo_id)
                results_summary = Entrez.read(handle_summary)
                for geo_summary in results_summary:
                    ftp = geo_summary['FTPLink']
                    break
                handle_summary.close()
            url = urlparse(ftp)
            ftp_url = url.netloc
            ftp_path = os.path.join(url.path, "soft/")
            handle.close()

        return ftp_url, ftp_path

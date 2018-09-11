import sqlite3

from command.lib.coll.platform.base_mapper import BaseMapper, sync_sqlite


class BlastFilter:

    @staticmethod
    def filter(splitted_blast_line, align_len, gap_open, mism):
        al = (float(splitted_blast_line[3]) / float(splitted_blast_line[12])) * 100.0;
        mm = int(splitted_blast_line[4])
        go = int(splitted_blast_line[5])
        return al >= align_len and mm <= mism and go <= gap_open

    @staticmethod
    def set_pass_sensitivity_uniqueness(sts, val):  # [gene, pass_sen, sen_unique, pass_spe]
        sts[1] = True
        sts[2] = val
        sts[3] = sts[3] and val

    @staticmethod
    def set_pass_specificity(sts, val):  # [gene, pass_sen, sen_unique, pass_spe]
        sts[1] = True
        sts[2] = True
        sts[3] = val

    @staticmethod
    def set_reject_sensitivity_uniqueness(sts, val):  # [gene, pass_sen, sen_unique, pass_spe]
        sts[1] = False
        sts[2] = val
        sts[3] = False


class MicroarrayMapper(BaseMapper):

    CREATE_SQL_STATS = '''
        CREATE TABLE IF NOT EXISTS stats (
          id INTEGER PRIMARY KEY,
          total_aligned_genes INTEGER DEFAULT 0,
          total_aligned_probes INTEGER DEFAULT 0,
          status TEXT DEFAULT 'running'
        )
    '''

    CREATE_SQL_ALIGNMENT_PARAMS = '''
            CREATE TABLE IF NOT EXISTS alignment_params (
              id INTEGER PRIMARY KEY,
              alignment_identity FLOAT DEFAULT 0,
              use_short_blastn INT DEFAULT 1
            )
        '''

    CREATE_SQL_FILTER_PARAMS = '''
                CREATE TABLE IF NOT EXISTS filter_params (
                  id INTEGER PRIMARY KEY,
                  alignment_length_1 INT DEFAULT 0,
                  gap_open_1 INT DEFAULT 0,
                  mismatches_1 INT DEFAULT 0,
                  alignment_length_2 INT DEFAULT 0,
                  gap_open_2 INT DEFAULT 0,
                  mismatches_2 INT DEFAULT 0,
                  status TEXT DEFAULT 'running'
                )
            '''

    CREATE_SQL_FILTER_STATS = '''
                    CREATE TABLE IF NOT EXISTS filter_stats (
                      id INTEGER PRIMARY KEY,
                      filter_params_fk INTEGER,
                      gene_unique_pass_sensitivity INT DEFAULT 0,
                      probe_unique_pass_sensitivity INT DEFAULT 0,
                      gene_non_unique_pass_sensitivity INT DEFAULT 0,
                      probe_non_unique_pass_sensitivity INT DEFAULT 0,
                      gene_unique_reject_sensitivity INT DEFAULT 0,
                      probe_unique_reject_sensitivity INT DEFAULT 0,
                      gene_non_unique_reject_sensitivity INT DEFAULT 0,
                      probe_non_unique_reject_sensitivity INT DEFAULT 0,
                      gene_pass_specificity INT DEFAULT 0,
                      probe_pass_specificity INT DEFAULT 0,
                      gene_reject_specificity INT DEFAULT 0,
                      probe_reject_specificity INT DEFAULT 0,
                      imported INT DEFAULT 0,
                      FOREIGN KEY(filter_params_fk) REFERENCES filter_params(id) ON DELETE CASCADE
                    )
                '''

    CREATE_SQL_FILTER_RESULT = '''
                        CREATE TABLE IF NOT EXISTS filter_result (
                          id INTEGER PRIMARY KEY,
                          filter_params_fk INTEGER,
                          probe_id INT,
                          gene_id INT,
                          pass_sen INT DEFAULT 0,
                          sen_unique INT DEFAULT 0,
                          pass_spe INT DEFAULT 0,
                          FOREIGN KEY(filter_params_fk) REFERENCES filter_params(id) ON DELETE CASCADE 
                        )
                    '''

    def __init__(self, blast_filename):
        self.blast_filename = blast_filename
        self.sqlite_filename = blast_filename.replace('.blast', '.sqlite')

    def __dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    @sync_sqlite
    def create_db(self, alignment_identity, use_short_blastn):
        probes = set()
        genes = set()
        with open(self.blast_filename, 'r') as blast_file:
            for line in blast_file:
                s = line.strip().split()
                probes.add(s[0])
                genes.add(s[1])
        con = sqlite3.connect(self.sqlite_filename)
        cur = con.cursor()
        cur.execute(MicroarrayMapper.CREATE_SQL_STATS)
        cur.execute(MicroarrayMapper.CREATE_SQL_ALIGNMENT_PARAMS)
        cur.execute(MicroarrayMapper.CREATE_SQL_FILTER_PARAMS)
        cur.execute(MicroarrayMapper.CREATE_SQL_FILTER_STATS)
        cur.execute(MicroarrayMapper.CREATE_SQL_FILTER_RESULT)
        cur.execute('DELETE FROM stats')
        cur.execute('DELETE FROM alignment_params')
        con.commit()
        query = 'INSERT INTO stats(total_aligned_genes, total_aligned_probes) VALUES (?, ?)'
        cur.execute(query, (len(genes), len(probes)))
        query = 'INSERT INTO alignment_params(alignment_identity, use_short_blastn) VALUES (?, ?)'
        cur.execute(query, (alignment_identity, int(use_short_blastn)))
        con.commit()
        con.close()

    @sync_sqlite
    def set_imported(self, imported, filter_stats_id=None):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()

        if filter_stats_id:
            cur.execute('UPDATE filter_stats SET imported=? WHERE id=?', (imported, filter_stats_id))
        else:
            cur.execute('UPDATE filter_stats SET imported=?', (imported,))

        con.commit()
        cur.close()
        con.close()

    @sync_sqlite
    def get_mapping_details(self):
        d = {
            'total_aligned': -1
        }
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        cur.execute('SELECT * FROM stats')
        rows = cur.fetchall()
        for row in rows:
            d['total_aligned'] = 'G: ' + str(row['total_aligned_genes']) + ', P: ' + str(row['total_aligned_probes'])
        con.close()
        return d

    @sync_sqlite
    def get_alignment_status(self):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        status = ''
        cur.execute('SELECT * FROM stats')
        rows = cur.fetchall()
        for row in rows:
            status = row['status']
        con.commit()
        cur.close()
        con.close()
        return status

    @sync_sqlite
    def set_filter_status(self, filter_params_id, status):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()

        cur.execute('UPDATE filter_params SET status=? WHERE id=?', (status, filter_params_id))

        con.commit()
        cur.close()
        con.close()

    @sync_sqlite
    def set_alignment_status(self, status):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        results = {}
        idd = 0
        cur.execute('SELECT * FROM stats')
        rows = cur.fetchall()
        for row in rows:
            idd = row['id']

        cur.execute('UPDATE stats SET status=? WHERE id=?', (status, idd))

        con.commit()
        cur.close()
        con.close()

    @sync_sqlite
    def get_alignment_params(self):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        results = {}
        cur.execute('SELECT * FROM alignment_params')
        rows = cur.fetchall()
        for row in rows:
            results = dict(row)

        con.commit()
        cur.close()
        con.close()
        return results

    @sync_sqlite
    def get_filter_params(self, filter_id):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        results = {}
        cur.execute('SELECT * FROM filter_params WHERE id = ?', (filter_id,))
        rows = cur.fetchall()
        for row in rows:
            results = dict(row)

        con.commit()
        cur.close()
        con.close()
        return results

    @sync_sqlite
    def __get_filter_details(self):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        results = []
        cur.execute("SELECT * FROM filter_stats")
        rows = cur.fetchall()
        for row in rows:
            results.append({
                'id': row['filter_params_fk'],
                'filter_params': self.get_filter_params(row['filter_params_fk']),
                'imported': bool(row['imported']),
                'non_unique_pass_sensitivity': 'G: ' + str(row['gene_non_unique_pass_sensitivity']) +
                                               ', P: ' + str(row['probe_non_unique_pass_sensitivity']),
                'unique_reject_sensitivity': 'G: ' + str(row['gene_unique_reject_sensitivity']) +
                                               ', P: ' + str(row['probe_unique_reject_sensitivity']),
                'non_unique_reject_sensitivity': 'G: ' + str(row['gene_non_unique_reject_sensitivity']) +
                                               ', P: ' + str(row['probe_non_unique_reject_sensitivity']),
                'unique_pass_sensitivity': 'G: ' + str(row['gene_unique_pass_sensitivity']) +
                                               ', P: ' + str(row['probe_unique_pass_sensitivity']),
                'pass_specificity': 'G: ' + str(row['gene_pass_specificity']) +
                                               ', P: ' + str(row['probe_pass_specificity']),
                'reject_specificity': 'G: ' + str(row['gene_reject_specificity']) +
                                    ', P: ' + str(row['probe_reject_specificity']),
            })
        cur.close()
        con.close()
        return results

    @sync_sqlite
    def get_filter_details(self):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        results = []
        details = {}
        cur.execute("SELECT * FROM filter_stats")
        rows = cur.fetchall()
        for row in rows:
            details[row['filter_params_fk']] = {
                'imported': bool(row['imported']),
                'non_unique_pass_sensitivity': 'G:' + str(row['gene_non_unique_pass_sensitivity']) +
                                               ',P:' + str(row['probe_non_unique_pass_sensitivity']),
                'unique_reject_sensitivity': 'G:' + str(row['gene_unique_reject_sensitivity']) +
                                             ',P:' + str(row['probe_unique_reject_sensitivity']),
                'non_unique_reject_sensitivity': 'G:' + str(row['gene_non_unique_reject_sensitivity']) +
                                                 ',P:' + str(row['probe_non_unique_reject_sensitivity']),
                'unique_pass_sensitivity': 'G:' + str(row['gene_unique_pass_sensitivity']) +
                                           ',P:' + str(row['probe_unique_pass_sensitivity']),
                'pass_specificity': 'G:' + str(row['gene_pass_specificity']) +
                                    ',P:' + str(row['probe_pass_specificity']),
                'reject_specificity': 'G:' + str(row['gene_reject_specificity']) +
                                      ',P:' + str(row['probe_reject_specificity']),
                }
        cur.execute("SELECT * FROM filter_params")
        rows = cur.fetchall()
        for row in rows:
            results.append({
                'id': row['id'],
                'filter_params': self.get_filter_params(row['id']),
                'imported': False if row['id'] not in details else details[row['id']]['imported'],
                'non_unique_pass_sensitivity': 'G:0,P:0' if row['id'] not in details else details[row['id']]['non_unique_pass_sensitivity'],
                'unique_reject_sensitivity': 'G:0,P:0' if row['id'] not in details else details[row['id']]['unique_reject_sensitivity'],
                'non_unique_reject_sensitivity': 'G:0,P:0' if row['id'] not in details else details[row['id']]['non_unique_reject_sensitivity'],
                'unique_pass_sensitivity': 'G:0,P:0' if row['id'] not in details else details[row['id']]['unique_pass_sensitivity'],
                'pass_specificity': 'G:0,P:0' if row['id'] not in details else details[row['id']]['pass_specificity'],
                'reject_specificity': 'G:0,P:0' if row['id'] not in details else details[row['id']]['reject_specificity'],
            })
        cur.close()
        con.close()
        return results

    @sync_sqlite
    def delete_filter_db(self, filter_id):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        con.execute("PRAGMA foreign_keys = ON")
        cur.execute('DELETE FROM filter_params WHERE id = ?', (filter_id, ))

        con.commit()
        cur.close()
        con.close()

    @sync_sqlite
    def write_filter_stats_db(self, filter_params_id):
        con = sqlite3.connect(self.sqlite_filename)
        con.row_factory = self.__dict_factory
        cur = con.cursor()
        gene_unique_pass_sensitivity = 0
        cur.execute("SELECT count(distinct(gene_id)) AS result FROM filter_result WHERE pass_sen > 0 AND sen_unique > 0")
        rows = cur.fetchall()
        for row in rows:
            gene_unique_pass_sensitivity = row['result']

        probe_unique_pass_sensitivity = 0
        cur.execute("SELECT count(distinct(probe_id)) AS result FROM filter_result WHERE pass_sen > 0 AND sen_unique > 0")
        rows = cur.fetchall()
        for row in rows:
            probe_unique_pass_sensitivity = row['result']

        gene_non_unique_pass_sensitivity = 0
        cur.execute("SELECT count(distinct(gene_id)) AS result FROM filter_result WHERE pass_sen > 0 AND sen_unique == 0")
        rows = cur.fetchall()
        for row in rows:
            gene_non_unique_pass_sensitivity = row['result']

        probe_non_unique_pass_sensitivity = 0
        cur.execute("SELECT count(distinct(probe_id)) AS result FROM filter_result WHERE pass_sen > 0 AND sen_unique == 0")
        rows = cur.fetchall()
        for row in rows:
            probe_non_unique_pass_sensitivity = row['result']

        gene_unique_reject_sensitivity = 0
        cur.execute("SELECT count(distinct(gene_id)) AS result FROM filter_result WHERE pass_sen == 0 AND sen_unique > 0")
        rows = cur.fetchall()
        for row in rows:
            gene_unique_reject_sensitivity = row['result']

        probe_unique_reject_sensitivity = 0
        cur.execute("SELECT count(distinct(probe_id)) AS result FROM filter_result WHERE pass_sen == 0 AND sen_unique > 0")
        rows = cur.fetchall()
        for row in rows:
            probe_unique_reject_sensitivity = row['result']

        gene_non_unique_reject_sensitivity = 0
        cur.execute("SELECT count(distinct(gene_id)) AS result FROM filter_result WHERE pass_sen == 0 AND sen_unique == 0")
        rows = cur.fetchall()
        for row in rows:
            gene_non_unique_reject_sensitivity = row['result']

        probe_non_unique_reject_sensitivity = 0
        cur.execute("SELECT count(distinct(probe_id)) AS result FROM filter_result WHERE pass_sen == 0 AND sen_unique == 0")
        rows = cur.fetchall()
        for row in rows:
            probe_non_unique_reject_sensitivity = row['result']

        gene_pass_specificity = 0
        cur.execute("SELECT count(distinct(gene_id)) AS result FROM filter_result WHERE pass_spe > 0")
        rows = cur.fetchall()
        for row in rows:
            gene_pass_specificity = row['result']

        probe_pass_specificity = 0
        cur.execute("SELECT count(distinct(probe_id)) AS result FROM filter_result WHERE pass_spe > 0")
        rows = cur.fetchall()
        for row in rows:
            probe_pass_specificity = row['result']

        gene_reject_specificity = 0
        cur.execute("SELECT count(distinct(gene_id)) AS result FROM filter_result WHERE pass_spe == 0 AND pass_sen > 0 AND sen_unique > 0")
        rows = cur.fetchall()
        for row in rows:
            gene_reject_specificity = row['result']

        probe_reject_specificity = 0
        cur.execute("SELECT count(distinct(probe_id)) AS result FROM filter_result WHERE pass_spe == 0 AND pass_sen > 0 AND sen_unique > 0")
        rows = cur.fetchall()
        for row in rows:
            probe_reject_specificity = row['result']

        cur.execute('''
            INSERT INTO filter_stats(filter_params_fk, gene_unique_pass_sensitivity, probe_unique_pass_sensitivity, 
            gene_non_unique_pass_sensitivity, probe_non_unique_pass_sensitivity, gene_unique_reject_sensitivity,
            probe_unique_reject_sensitivity, gene_non_unique_reject_sensitivity, probe_non_unique_reject_sensitivity,
            gene_pass_specificity, probe_pass_specificity, gene_reject_specificity, probe_reject_specificity) 
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (filter_params_id, gene_unique_pass_sensitivity, probe_unique_pass_sensitivity,
                    gene_non_unique_pass_sensitivity, probe_non_unique_pass_sensitivity, gene_unique_reject_sensitivity,
                    probe_unique_reject_sensitivity, gene_non_unique_reject_sensitivity, probe_non_unique_reject_sensitivity,
                    gene_pass_specificity, probe_pass_specificity, gene_reject_specificity, probe_reject_specificity))

        con.commit()
        cur.close()
        con.close()

    @sync_sqlite
    def write_filter_db(self, filter_params_id, result):
        con = sqlite3.connect(self.sqlite_filename)
        cur = con.cursor()
        res = []
        for probe_id, rr in result.items():
            for r in rr:
                t = tuple([filter_params_id, probe_id] + r)
                res.append(t)
        cur.executemany('''
            INSERT INTO filter_result(filter_params_fk, probe_id, gene_id,
                                      pass_sen, sen_unique, pass_spe) 
            VALUES(?, ?, ?, ?, ?, ?)
            ''', res)
        con.commit()
        cur.close()
        con.close()

    @sync_sqlite
    def write_params_db(self, alignment_length_1, gap_open_1, mismatches_1,
               alignment_length_2, gap_open_2, mismatches_2):
        con = sqlite3.connect(self.sqlite_filename)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO filter_params(alignment_length_1, gap_open_1, mismatches_1,
               alignment_length_2, gap_open_2, mismatches_2) 
            VALUES(?, ?, ?, ?, ?, ?)
            ''', (alignment_length_1, gap_open_1, mismatches_1,
               alignment_length_2, gap_open_2, mismatches_2))
        rowid = cur.lastrowid
        con.commit()
        cur.close()
        con.close()
        return rowid

    @sync_sqlite
    def get_filter_result_count(self):
        con = sqlite3.connect(self.sqlite_filename)
        cur = con.cursor()
        cur.execute('SELECT count(*) FROM filter_result WHERE pass_spe=1')
        rows = cur.fetchall()
        results = 0
        for row in rows:
            results = row[0]
        con.commit()
        cur.close()
        con.close()

        return results

    @sync_sqlite
    def get_filter_result_dict(self, filter_id, start, end, abortable_fun=lambda: False):
        con = sqlite3.connect(self.sqlite_filename)
        cur = con.cursor()
        cur.execute('''
                    SELECT * FROM filter_result WHERE filter_params_fk=? AND pass_spe=1 ORDER BY id LIMIT ? OFFSET ?
                    ''', (filter_id, (end - start), start))
        rows = cur.fetchall()
        results = {}
        for row in rows:
            if abortable_fun():
                break
            results[row[2]] = row[3]
        con.commit()
        cur.close()
        con.close()

        return results

    @sync_sqlite
    def filter(self, filter_params_id, abortable_fun=lambda: False):
        if abortable_fun():
            return
        res = {}
        chunk_size = 10000
        line_counter = 0
        filter_params = self.get_filter_params(filter_params_id)

        alignment_length_1 = filter_params['alignment_length_1']
        gap_open_1 = filter_params['gap_open_1']
        mismatches_1 = filter_params['mismatches_1']
        alignment_length_2 = filter_params['alignment_length_2']
        gap_open_2 = filter_params['gap_open_2']
        mismatches_2  = filter_params['mismatches_2']
        with open(self.blast_filename) as f:
            for l in f:
                if abortable_fun():
                    break
                line_counter += 1
                s = l.strip().split()
                probe_id = s[0]
                gene_id = s[1]
                struct = [gene_id, False, False, False]  # create default struct [gene, pass_sen, sen_unique, pass_spe]
                if probe_id not in res:
                    if line_counter >= chunk_size:
                        self.write_filter_db(filter_params_id, res)
                        res.clear()
                        line_counter = 0
                    res[probe_id] = []
                res[probe_id].append(struct)

                sen = BlastFilter.filter(s, alignment_length_1, gap_open_1, mismatches_1)
                spe = BlastFilter.filter(s, alignment_length_2, gap_open_2, mismatches_2)
                if sen:  # sensitivity
                    # check uniqueness
                    probe_genes_pass_sen = 0
                    for sts in res[probe_id]:
                        if sts[1] and sts[0] != gene_id:  # if it align twice on the same gene is fine
                            probe_genes_pass_sen += 1
                            break
                    if probe_genes_pass_sen > 0:  # sensitivity non unique
                        for sts in res[probe_id]:
                            BlastFilter.set_pass_sensitivity_uniqueness(sts, False)
                        BlastFilter.set_pass_sensitivity_uniqueness(struct, False)
                    else:  # sensitivity unique
                        BlastFilter.set_pass_specificity(struct, spe)
                else:  # reject sensitivity
                    probe_genes_reject_sen = 0
                    for sts in res[probe_id]:
                        if not sts[1] and sts[0] != gene_id:
                            probe_genes_reject_sen += 1
                            break
                    if probe_genes_reject_sen > 0:  # reject sensitivity non unique
                        for sts in res[probe_id]:
                            if not sts[1]:
                                BlastFilter.set_reject_sensitivity_uniqueness(sts, False)
                    else:
                        BlastFilter.set_reject_sensitivity_uniqueness(struct, True)
        self.write_filter_db(filter_params_id, res)
        self.write_filter_stats_db(filter_params_id)

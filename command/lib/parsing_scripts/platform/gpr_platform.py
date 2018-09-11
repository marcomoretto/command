# Get info from passed input
#   SCRIPT_PARAMETERS[0] - number of lines to skip
#   SCRIPT_PARAMETERS[1] - the column header(s) to parse out the DB 'org_probe_id' field; if multiple seperate with a pipe | (actual probe ids will be concatenated with dots . in that case)
#   SCRIPT_PARAMETERS[2] - the column header of the probe sequence you want to parse out
#   SCRIPT_PARAMETERS[3] - the column header to parse out the DB 'gene_map_content' field; if multiple seperate with a pipe | (actual probe ids will be concatenated with dots . in that case)
#   SCRIPT_PARAMETERS[4] - the column header to parse out the DB 'probe_name' field; if multiple seperate with a pipe | (actual probe ids will be concatenated with dots . in that case)
#   SCRIPT_PARAMETERS[5] - the column header to parse out the DB 'probe_set_name' field
#   SCRIPT_PARAMETERS[6] - to ensure that org_probe_id in SAMPLE_OBJECT will be unique (defaults to False)

# We need a nice way to escape special characters here!!!
def dequote(l_str):
    return [x[1:-1] for x in l_str if x[0] == "\"" or x[0] == "'"]

access_id = ENTITY_NAME
#SCRIPT_PARAMETERS = SCRIPT_PARAMETERS.replace('"','')
#PARAMETERS = SCRIPT_PARAMETERS.split(',')
for i in range(7):          # Note: will loop 0,1,2,3,4,5,6
    if len(PARAMETERS)<=i:
        PARAMETERS.append('')
nr_lines_skip = int(PARAMETERS[0])        
id_field = [x for x in PARAMETERS[1].split('|') if x != ''] # Always a list to allow concatenating multiple fields
seq_field = PARAMETERS[2]
map_field = [x for x in PARAMETERS[3].split('|') if x != ''] # Always a list to allow concatenating multiple fields
name_field = [x for x in PARAMETERS[4].split('|') if x != ''] # Always a list to allow concatenating multiple fields
ps_field = PARAMETERS[5]
unique_probes = bool(PARAMETERS[6]) and PARAMETERS[6]!='False' and PARAMETERS[6]!='0'    # If it's an empty string, 0, or False it will be False (however, if you pass 'False' or '0' as argument it's a string and will be True, so therefor the end :D) 
present_probe_id = set()        # Technically only necessary if unique_probes==True, but nicer code this way
PLATFORM_OBJECT.platform_type = 'microarray'
f = open(INPUT_FILE,'rU')
# Move the cursor down nr_lines_skip...
header = []
# ...and from there loop through the rest    
id_index = []
for l in f:
    if l.strip()=='' or nr_lines_skip > 0:
        nr_lines_skip -= 1
        continue
    if len(header)==0:
        esc_l = l.replace('"','') # Python3 is unicode by default!
        header = [x.strip() for x in esc_l.split('\t')]
        id_index = [header.index(i) for i in id_field]
        if seq_field!='':
            seq_index = header.index(seq_field)
        if len(name_field) > 0:
            name_index = [header.index(i) for i in name_field]
        if len(map_field) > 0:
            map_index = [header.index(i) for i in map_field]
        if ps_field!='':    
            ps_index = header.index(ps_field)
        continue
    row = l.split('\t')
    org_probe_id = [row[i].replace('"','').strip() for i in id_index]
    probe_seq = ''
    if seq_field!='':
        probe_seq = row[seq_index].replace('"','')
    probe_name = '' 
    if len(name_field) > 0:
        probe_name = [row[i].replace('"','') for i in name_index]
    gene_map_content = ''
    if len(map_field) > 0:
        gene_map_content = [row[i].replace('"','') for i in map_index]
    probe_set_name = ''
    if ps_field!='':
        probe_set_name = row[ps_index].replace('"','')
    if unique_probes and '.'.join(org_probe_id) in present_probe_id:
        continue
    PLATFORM_OBJECT.add_bio_feature_reporter_data('.'.join(org_probe_id), '.'.join(org_probe_id), sequence=probe_seq, probe_access_id='.'.join(probe_name),
        probe_set_name=probe_set_name)
    present_probe_id.add('.'.join(org_probe_id))
f.close()
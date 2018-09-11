import re

# Get info from passed input
#   SCRIPT_PARAMETERS[0] - number of lines to skip, overrides the default of one
#   Need to include other potential overrides???

# Initializations and defaults
trailingN = re.compile('N+$')   # trailing N's
access_id = ENTITY_NAME
#SCRIPT_PARAMETERS = SCRIPT_PARAMETERS.replace('"','')
#PARAMETERS = SCRIPT_PARAMETERS.split(',')
if not PARAMETERS[0]:
    nr_lines_skip = 0
else:
    nr_lines_skip = int(PARAMETERS[0])

f = open(INPUT_FILE)
header = []
probe_ind = -1
value_ind = -1
for l in f:
    # Move the cursor down nr_lines_skip, ...
    if nr_lines_skip > 0:
        nr_lines_skip -= 1
        continue
    # ...then get the header, ...
    if len(header)==0:
        esc_l = l.replace('"','') # Python3 is unicode by default!
        header = esc_l.rstrip().split('\t')
        continue
    # ...and from there loop through the rest 
    row = l.rstrip().split('\t')
    # NOTE: org_probe_id and probe_type ('NA' or 'PM') are MANDATORY!!!
    org_probe_id = row[header.index('X')]+'.'+row[header.index('Y')]
    probe_type = 'NA'
    tmp_seq = row[header.index('PROBE_SEQUENCE')]         
    probe_seq = trailingN.sub('',tmp_seq)         # Remove trailing N's if present
    probe_name = row[header.index('PROBE_ID')]
    gene_map_content = row[header.index('PROBE_DESIGN_ID')]     # Or just the DESIGN_ID as this on includes the X and Y in the string
    probe_set_name = row[header.index('SEQ_ID')]
    PLATFORM_OBJECT.add_bio_feature_reporter_data(org_probe_id, probe_type, 
    sequence=probe_seq, probe_name=probe_name, gene_map_content=gene_map_content, probe_set_name=probe_set_name)
f.close()

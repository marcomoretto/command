# Get info from passed input
#   SCRIPT_PARAMETERS[0] - number of lines to skip, overrides the default of 1
#   SCRIPT_PARAMETERS[1] - temporary override for original platform in case structuring assignments don't stick

# Initializations and defaults
access_id = ENTITY_NAME.split('.')[0]
channel = ENTITY_NAME.split('.ch')[1]
#SCRIPT_PARAMETERS = SCRIPT_PARAMETERS.replace('"','')
#PARAMETERS = SCRIPT_PARAMETERS.split(',')
for i in range(2):        
    if len(PARAMETERS)<=i:
        PARAMETERS.append('')
if not PARAMETERS[0]:
    nr_lines_skip = 1
else:
    nr_lines_skip = int(PARAMETERS[0])
SAMPLE_OBJECT.org_platform_access_id = PARAMETERS[1]
    
# What if there are more than one channel on the Nimblegen???    

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
        esc_l = l.replace('"','') # python 3 it is unicode by default!
        header = esc_l.rstrip().split('\t')
        continue
    # ...and from there loop through the rest 
    row = l.rstrip().split('\t')
    probe_id = row[header.index('X')]+'.'+row[header.index('Y')]
    value = row[header.index('PM')]     # OR should I add together the MM value too in case it's that kind of probe (se Nimblegen file descriptions)
    SAMPLE_OBJECT.add_raw_data(probe_id, value)
f.close()

from soft_file_parser import SoftFile
from column_identifier import sample_column_identifier
from utils import get_dict_key_from_value

soft = SoftFile(INPUT_FILE)
soft.parse()

access_id = ENTITY_NAME.split('.')[0]  
channel = ENTITY_NAME.split('.ch')[1]
value_field = PARAMETERS[0] if len(PARAMETERS) > 0 else None

# If there is no value field parsed, don't parse the data table
parse_data_table = value_field != ''

SAMPLE_OBJECT.sample_name = ENTITY_NAME
if hasattr(soft.samples[access_id], 'Sample_description'):
    if type(soft.samples[access_id].Sample_description) == list:
        SAMPLE_OBJECT.description = ' '.join(soft.samples[access_id].Sample_description)
if hasattr(soft.samples[access_id], 'Sample_label_ch' + channel):
    SAMPLE_OBJECT.channel_label = getattr(soft.samples[access_id], 'Sample_label_ch' + channel)

if parse_data_table:
    # If the value field is 'AUTO' then attempt an automatic column identification first
    if value_field == 'AUTO':
        # 1. Check the column header names and output log in case of hit
        header = next(soft.samples[ENTITY_NAME[:-4]].table_data, {}).keys()
        identified_field = sample_column_identifier(SAMPLE_OBJECT.channel_label, header)
        print(header, identified_field)
        if identified_field and len(identified_field) == 1:
            value_field = identified_field[0]
            print('<b>'+ENTITY_NAME+'</b>:',os.path.basename(INPUT_FILENAME)+' identified <b>'+value_field+'</b> for channel label <b>'+SAMPLE_OBJECT.channel_label+'</b>')

    # If the identification worked, or a value_field is given (i.e. not AUTO), do the parsing
    if value_field != 'AUTO':
        for row in soft.samples[ENTITY_NAME[:-4]].table_data:
            id = row['ID_REF']
            val = row[value_field]
            SAMPLE_OBJECT.add_raw_data(id, val)

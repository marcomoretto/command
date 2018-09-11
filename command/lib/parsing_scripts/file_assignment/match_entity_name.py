def assign(input_files, entity, entity_type, parameters):
    files = []
    name = ''
    if entity_type == 'sample':
        name = entity['sample_name'].split('.ch')[0]
    elif entity_type == 'platform':
        name = entity['platform_access_id']
    elif entity_type == 'experiment':
        name = entity['experiment_access_id']
    for f in input_files:
        if name in f:
            files.append(f)
            break
    return files

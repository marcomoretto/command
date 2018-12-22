def assign(input_files, entity, entity_type, parameters):
    """Assign the selected input files (or all the files if checked) to every ENTITY with matching NAME

    For each ENTITY (experiment, platforms or samples) for which a parsing script is selected, only the (selected)
    input files with a name that match the one of the entity will be assinged
    (for example a file name GSE123.soft would match the experiment entity GSE123).

    PARAMETERS:
        None

    """
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

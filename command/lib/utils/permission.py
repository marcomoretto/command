import collections


class Permission:
    COMPENDIUM_ACCESS = 'compendium_access'
    USE_PYTHON_EDITOR = 'use_python_editor'
    REPORTER_MAPPING = 'reporter_mapping'
    DOWNLOAD_UPLOAD_EXPERIMENT = 'download_upload_experiment'
    DELETE_EXPERIMENT = 'delete_experiments'
    PARSE_EXPERIMENT = 'parse_experiment'
    IMPORT_EXPERIMENT = 'import_experiment'
    DELETE_PLATFORM = 'delete_platform'
    DELETE_BIOFEATURE = 'delete_biofeature'
    ADD_BIOFEATURE = 'add_biofeature'
    DELETE_FILE = 'delete_file'
    IMPORT_PLATFORM = 'import_platform'
    DELETE_PARSING_DATA = 'delete_parsing_data'
    EXPORT_COMPENDIUM = 'export_compendium'

    names = collections.OrderedDict({
        COMPENDIUM_ACCESS: 'Access compendium',
        USE_PYTHON_EDITOR: 'Use Python editor',
        REPORTER_MAPPING: 'Map reporters to bio features',
        DOWNLOAD_UPLOAD_EXPERIMENT: 'Download/upload experiment',
        PARSE_EXPERIMENT: 'Parse experiment',
        IMPORT_EXPERIMENT: 'Import experiment',
        DELETE_EXPERIMENT: 'Delete experiments',
        ADD_BIOFEATURE: 'Add bio features',
        DELETE_BIOFEATURE: 'Delete biofeatures',
        DELETE_PLATFORM: 'Delete platform',
        IMPORT_PLATFORM: 'Import platform',
        DELETE_PARSING_DATA: 'Delete parsing (temp) data',
        EXPORT_COMPENDIUM: 'Export compendium',
        DELETE_FILE: 'Delete experiment files'
    })

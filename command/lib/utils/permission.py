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
    ONTOLOGIES = 'ontologies'
    BIO_FEATURE_ANNOTATION = 'bio_feature_annotation'
    IMPORT_BIO_FEATURE_ANNOTATION = 'import_bio_feature_annotation'
    DELETE_BIO_FEATURE_ANNOTATION = 'delete_bio_feature_annotation'
    CREATE_ONTOLOGY = 'create_ontology'
    MODIFY_ONTOLOGY = 'modify_ontology'
    DELETE_ONTOLOGY = 'delete_ontology'
    JUPYTER_NOTEBOOK = 'jupyter_notebook'
    NORMALIZATION_MANAGER = 'normalization_manager'
    CREATE_NORMALIZATION = 'create_normalization'
    MODIFY_NORMALIZATION = 'modify_normalization'
    DELETE_NORMALIZATION = 'delete_normalization'
    VIEW_EXPERIMENT_NORMALIZATION = 'view_experiment_normalization'
    MODIFY_EXPERIMENTAL_DESIGN = 'modify_experimental_design'
    NORMALIZE_EXPERIMENT = 'normalize_experiment'

    names = collections.OrderedDict({
        'Compendium access': collections.OrderedDict({
            COMPENDIUM_ACCESS: 'Access compendium'
        }),
        'Data collection': collections.OrderedDict({
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
        }),
        'Annotation': collections.OrderedDict({
            ONTOLOGIES: 'View ontologies',
            BIO_FEATURE_ANNOTATION: 'View biological feature annotation',
            IMPORT_BIO_FEATURE_ANNOTATION: 'Import biological feature annotation',
            DELETE_BIO_FEATURE_ANNOTATION: 'Delete biological feature annotation',
            CREATE_ONTOLOGY: 'Create ontology',
            MODIFY_ONTOLOGY: 'Modify ontology',
            DELETE_ONTOLOGY: 'Delete ontology'
        }),
        'Normalization': collections.OrderedDict({
            JUPYTER_NOTEBOOK: 'Jupyter notebook',
            NORMALIZATION_MANAGER: 'Normalization manager',
            CREATE_NORMALIZATION: 'Create normalization',
            MODIFY_NORMALIZATION: 'Modify normalization',
            DELETE_NORMALIZATION: 'Delete normalization',
            VIEW_EXPERIMENT_NORMALIZATION: 'View experiment normalization',
            NORMALIZE_EXPERIMENT: 'Normalize experiment',
            MODIFY_EXPERIMENTAL_DESIGN: 'Modify experimental design'
        })
    })

    @staticmethod
    def get_name(name):
        for k, v in Permission.names.items():
            for x, y in v.items():
                if name == x:
                    return y
        return None

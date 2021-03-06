'''
The Experiment Object, Platform Object and Sample Object are Python objects used as proxy to import a new experiment in the database

The file name of the experiment, platform or sample is stored in the variable named **INPUT_FILE**
The name of the entity (experiment, platform or sample name) is stored in the variable named **ENTITY_NAME**
To access parameters passed to each script use the list **PARAMETERS**
Within each entity (experiment, platform or sample) you can choose the execution order of the script using the Order column.

To access Experiment Object use the **EXPERIMENT_OBJECT** variable in the Python script used with experiment files.

EXPERIMENT_OBJECT variables
---------------------------

**EXPERIMENT_OBJECT**.experiment_access_id: (string) the experiment access id
**EXPERIMENT_OBJECT**.experiment_name: (string) the experiment name
**EXPERIMENT_OBJECT**.scientific_paper_ref: (string) pubblication associated to the experiment
**EXPERIMENT_OBJECT**.description: (string) the experiment description

To access Platform Object use the **PLATFORM_OBJECT** variable in the Python script used with platform files.

PLATFORM_OBJECT variables
-------------------------

**PLATFORM_OBJECT**.platform_access_id (string) the platform access id
**PLATFORM_OBJECT**.platform_name (string) the platform name
**PLATFORM_OBJECT**.platform_type (string) 'microarray or rna-seq'
**PLATFORM_OBJECT**.description (string) the platform description
**PLATFORM_OBJECT**.add_bio_feature_reporter_data(name, description, **kwargs): add a reporter to the platform

**kwargs are platform_type dependent. i.e. for 'microarray' they are probe_access_id,
probe_set_name, probe_type and sequence

To access Sample Object use the **SAMPLE_OBJECT** variable in the Python script used with sample files.

SAMPLE_OBJECT variables and methods
-----------------------------------

**SAMPLE_OBJECT**.sample_name (string) the sample name
**SAMPLE_OBJECT**.description (string) the sample description
**SAMPLE_OBJECT**.add_raw_data(bio_feature_reporter_name, value): add raw data of this sample
'''
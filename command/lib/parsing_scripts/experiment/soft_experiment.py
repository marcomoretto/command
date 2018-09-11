from soft_file_parser import SoftFile

soft = SoftFile(INPUT_FILE)
soft.parse()

for k, v in soft.series.items():
    EXPERIMENT_OBJECT.experiment_access_id = str(k)
    EXPERIMENT_OBJECT.experiment_name = v.Series_title
    EXPERIMENT_OBJECT.scientific_paper_ref = v.Series_pubmed_id
    EXPERIMENT_OBJECT.description = "\n".join(v.Series_summary)
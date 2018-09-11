What is COMMAND>_?
==================

COMMAND>_ is an acronym that stands for **COM**\pendia **MAN**\agement **D**\esktop. It is the software used for the creation of several gene expression compendia such as COLOMBOS [#f1]_ and VESPUCCI [#f2]_. Despite being used since 2010 it has been made publicly available for anyone to use only in 2018, after having been completely rewritten.
COMMAND>_ was originally conceived for the collection (and integration) of prokaryotes microarray experiments. As time goes by it has been evolved to allow also RNA-seq experiment to be imported and other species to be managed.
With the current implementation COMMAND>_ is still meant for gene expression data collection but can be easily extended to support other kind of quantitative measurement technology (have a look at :doc:`for_developers`).

COMMAND>_ is a Python web application developed using the `Django <https://www.djangoproject.com/>`_ framework for the backend, while the web interface has been developed using `ExtJS <https://www.sencha.com/products/extjs/#overview>`_ with a look and feel typical of desktop applications. With COMMAND>_ you can search and download experiment from public gene expression databases, such as `GEO <https://www.ncbi.nlm.nih.gov/gds>`_ , `ArrayExpress <https://www.ebi.ac.uk/arrayexpress/>`_ or `SRA <https://www.ncbi.nlm.nih.gov/sra>`_, parse downloaded files to extract only valuable information, preview parsed data and import experiment data into a database. The pivotal point is the usage of custom Python scripts to mine only the relevant information. Scripts can be created or modified directly within the interface and are responsible to parse input files and populate each part of the **data model** (see :doc:`database_schema`), i.e. measurement data and meta-data for *experiment*, *platforms* and *samples*.

For microarray platforms it would be necessary to map probes to genes but before this step genes have first to be imported. COMMAND>_ allow to perform both these steps. For the latter it would be simply a matter of uploading a FASTA file with gene sequences (see :doc:`data_collection`), while for the former a `BLAST <https://blast.ncbi.nlm.nih.gov/Blast.cgi>`_ alignment followed by a two-step filtering will be performed. In this way the microarray gets annotated with the latest available information enhancing the homogeneity since all microarrays will be annotated using the same gene list (see also :doc:`map_feature`).

.. rubric:: References

.. [#f1] Moretto, M. et al. (2015). COLOMBOS v3. 0: leveraging gene expression compendia for cross-species analyses. *Nucleic acids research*, 44(D1), D620-D623.
.. [#f2] Moretto, M. et al. (2016). VESPUCCI: exploring patterns of gene expression in grapevine. *Frontiers in plant science*, 7, 633.



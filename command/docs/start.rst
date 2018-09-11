Getting start with COMMAND>_
============================

Getting my user id and password
-------------------------------

You can log in to COMMAND>_ using:

- user_id: command
- password: command

Now you can change the admin password, create new users and assign them privileges following the instructions in :doc:`admin_user`.

.. _login:
.. figure::  _static/login.png
   :align:   center


Set up and select a compendium
------------------------------

The first thing to do is creating a new empty compendium. Go to Admin (top bar) > Compendium Manager > Create Compendium (bottom-left corner + icon) and follow the instructions at :doc:`admin_user`. <TO DO>

.. _comp01:
.. figure::  _static/comp01.png
   :align:   center

Now that a new compendium has been set up you need to retrieve a FASTA file containing the gene ids and sequences for the species you want to study.
_Tip_: Usually you can visit, for example, the NCBI Nucleotide database and get the coding sequences for the organism of interest. This file is mandatory for blasting and mapping respectively in either microarray or RNA-Seq experiments. In order to import it into COMMAND>_ go to Data collection (on the top-left corner) > Biological features, then select Import biological features from the bottom-left + icon.

.. _comp02:
.. figure::  _static/comp02.png
   :align:   center

Now your gene annotation file has been imported and you can start looking for interesting experiments (both microarray and RNA-Seq) related to the organism of interest.

.. _search_database:

Searching public databases
--------------------------

After a new empty compendium has been created and a species of interest selected the user can start looking for collections of samples (from one or more experiments) from public databases (GEO, ArrayExpress or, in case of RNA-Seq experiments, SRA):
Go to > Data collection (on the top-left corner) then > Experiments > New Experiment (on the bottom right corner) > from public DB.

.. _search01:
.. figure::  _static/search01.png
   :align:   center

- In the Search options field of the dialog 'Download from Public DB' select the DB (here GEO) and the term of interest, either a description (e.g. Leukemia b-cell, Vitis vinifera, erc.) or directly a GSE ID.
- From the list select an experiment of interest and click the download button(_Tip_: you can download multiple experiments at the same time).


.. _search02:
.. figure::  _static/search02.png
   :align:   center

- After a while, depending of the number of samples in the selected experiment(s) 


.. Tip::
	check Message log frequently) you have your experiment downloaded (Tip: inspect the Experiments section to see which experiments are available, yet to be parsed or already imported).

Now you can start parse and import some experiment (see :doc:`use_cases`).


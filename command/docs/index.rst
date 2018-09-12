.. COMMAND>_ documentation master file, created by
   sphinx-quickstart on Thu May 24 10:19:54 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. |email| image:: _static/email.png


Welcome to COMMAND>_'s documentation!
=====================================

COMMAND>_ is a web-based application used to download, collect and manage gene expression data from public databases.

Main features are.


* Easy installation and update using `Docker Compose <https://docs.docker.com/compose/install/>`_ technology.
* Graphical User Interface (GUI) for parsing and importing gene expression data.
* Default `Python <https://www.python.org/>`_ scripts for easy parsing/importing of the most common microarray platforms (Affymetrix, Nimblegen, two-colors, etc.) and dedicated scripting editor for allowing flexible importing of any kind of gene expression data.
* Automatic pre-processing (downloading, trimming, mapping and counting) of bulk RNA-Seq data.
* Exporting of the collected data.


.. note::

   Give it a try on https://command.fmach.it:4242 using:

   - username: ``guest``
   - password: ``demo``

   Check out the :doc:`use_cases`!



.. toctree::
   :maxdepth: 2
   :caption: Table of Contents

   what_is_command
   start
   message_log
   admin_user
   deploy
   database_schema
   use_cases
   for_developers


Contribute & Support
====================

Use the `GitHub Push Request and/or Issue Tracker <https://github.com/marcomoretto/command>`_.

Author
======

To send me an e-mail about anything else related to COMMAND>_ write to |email|

License
=======

The project is licensed under the `GPLv3 license <https://www.gnu.org/licenses/gpl-3.0.html>`_.

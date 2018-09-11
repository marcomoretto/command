Deploy
======

COMMAND>_ is a complex application and relies on several other software components to work. In order to ease up the deployment process a ``docker-compose.yml`` file is provided, so assuming you have a working `Docker Compose <https://docs.docker.com/compose/>`_ environment, the deployment process will be a matter of running a few commands.

In case you want to manually deploy COMMAND>_ in your environment there will be more steps you will need to take care of such as install all the dependencies.

Requirements
------------
Have a look at the ``requirements.txt`` file for details. COMMAND>_ main dependencies are:

 - `Python 3 <https://www.python.org/>`_
 - `Django <https://www.djangoproject.com/>`_
 - `PostgreSQL <https://www.postgresql.org/>`_
 - `Celery <http://www.celeryproject.org/>`_
 - `Channels <https://github.com/django/channels>`_
 - `Numpy <http://www.numpy.org/>`_
 - `Pandas <https://pandas.pydata.org/>`_
 - `BioPython <https://biopython.org/>`_

Docker Compose
--------------
Assuming that you have `Docker Compose correctly installed <https://docs.docker.com/compose/install/>`_, you should be able to perform the following steps:

.. code-block:: bash

   # 1. clone the repository
   git clone

   # 2. build
   docker-compose build

   # 3. start docker
   docker-compose up -d

   # 4. create database schema
   docker-compose exec web python manage.py migrate

   # 5. create admin user
   docker-compose exec web python manage.py init_admin

   # 6. create initial options
   docker-compose exec web python manage.py init_options

   # 7. create demo compendium
   docker-compose exec web python manage.py init_demo_compendium demo

   # 8. run daphne
   docker-compose exec -d daphne daphne -b 0.0.0.0 -p 8001 cport.asgi:channel_layer

   # 9. run worker
   docker-compose exec -d worker python3 manage.py runworker

That's it! You should be able to point your browser to http://localhost and login into COMMAND>_ using:
  - username: ``admin``
  - password: ``admin``

Manual Deploy
-------------
<TODO>

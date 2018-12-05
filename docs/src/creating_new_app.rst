.. _creating_new_app:

Running ``tcinit`` will create a new playbook or job app. To get use it, create a new directory for your app, navigate into the directory, and run ``tcinit`` as described below.

Usage
-----

.. code:: bash

    usage: tcinit [-h] [--branch {master,develop}]
                  [--action {create,update,migrate}] --type {job,playbook}
                  [--force]

    optional arguments:
      -h, --help            show this help message and exit
      --branch {master,develop}
                            Git branch.
      --action {create,update,migrate}
                            Whether a new app should be CREATED, an existing app
                            should be UPDATED, or an existing app of a different
                            format MIGRATED to the new version.
      --type {job,playbook}
                            Init a new App.
      --force               If true, this will overwrite existing files in a
                            directory to create a new app.

A new playbook app can be created with: ``tcinit --type playbook``.

A new job app can be created with: ``tcinit --type job``.

New App Layout
--------------

- ``README.md``: A README for the new app
- ``__main__.py``: TcEx file to make sure the app is run correctly - Do not edit
- ``app.py``: A class containing the code which will be executed when the app is run
- ``args.py``: A class to handle arguments
- ``install.json``: The `app configuration file <https://docs.threatconnect.com/en/latest/deployment_config.html>`__ for the app
- ``requirements.txt``: A list of the packages required for the app
- ``run.py``: File to run the app
- ``setup.cfg``: Setup config for the project
- ``tcex.json``: Configuration file for the new app (more details `here <https://docs.threatconnect.com/en/latest/tcex/building_apps.html#using-configuration-file>`__)
- ``tcex_json_schema.json``: TcEx file to make sure tcex.json is properly configured - Do not edit

**Playbook** apps created with ``tcinit --type playbook`` will have a ``playbook_app.py`` file which serves as a parent class for the ``App`` class in ``app.py``. **Job** apps created with ``tcinit --type job`` will have a ``job_app.py`` file which serves as a parent class for the ``App`` class in ``app.py``.

To get familiar with how your new app works, you'll want to take a look at ``run.py`` and ``app.py``. When writing a new app, most of the work will be done in ``app.py``.

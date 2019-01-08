.. _building_apps_structure:


Playbook App Structure
----------------------

.. code:: bash

    ├── .gitignore
    ├── .pre-commit-config.yaml
    ├── README.md
    ├── __main__.py
    ├── app.py
    ├── args.py
    ├── install.json
    ├── log
    │   ├── app.log
    │   ├── message.tc
    │   ├── run.log
    ├── playbook_app.py
    ├── pyproject.toml
    ├── requirements.txt
    ├── run.py
    ├── setup.cfg
    ├── tcex.d
    │   ├── data
    │   └── profiles
    │       └── simple_data.json
    ├── tcex.json
    └── tcex_json_schema.json

.gitignore (optional)
~~~~~~~~~~~~~~~~~~~~~

Template file that specifies intentionally untracked files that Git should ignore. This file is part of the template update, but can be optionally updated if required.

.pre-commit-config.yaml (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration file for the ``pre-commit`` Python command line tool. This configuration is the same one that is used for internal development of Apps.

README.md (required)
~~~~~~~~~~~~~~~~~~~~

The ``README.md`` file should contain any relevant information for the App and the App release notes.

__main__.py (required)
~~~~~~~~~~~~~~~~~~~~~~

Template file that should not be modified.

app.py (required)
~~~~~~~~~~~~~~~~~

This file contains the "main" App logic and contains the ``run()`` method that is called by default. It also can contain methods for **tc_actions**.

args.py (required)
~~~~~~~~~~~~~~~~~~

This file contains the args required for the App to function properly.  Only App args are required to be defined.  The default args are part of the TcEx framework and are added automatically.

install.json (required)
~~~~~~~~~~~~~~~~~~~~~~~

This is the main configuration file for the App and controls what inputs and outputs will be presented to the user.

log (temporary)
~~~~~~~~~~~~~~~

This directory is created when running testing profile locally. All App output is written to this directory as well as the output of the ``tcrun`` command.

log/app.log (temporary)
~~~~~~~~~~~~~~~~~~~~~~~

This log file contains the logging output of the App.

log/message.tc (temporary)
~~~~~~~~~~~~~~~~~~~~~~~~~~

This file contains the App exit message. The contents of this file will be displayed in the UI when the App is run in platform. For local testing the file should be verified to have content on successful App completion and on failure.

log/run.log (temporary)
~~~~~~~~~~~~~~~~~~~~~~~

This log file contains the output from the ``tcrun`` command and will contain information about validations rules.

playbook_app.py (required)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Template file that contains base logic for a Playbook App. This file should not be edited and will get updated when using ``tcprofile --action update --template <template name>`` command.

pyproject.toml (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~

This is a Python tool configuration file which contains the configuration for the "black" formatting tool used to format all Python code.

requirements.txt (required)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This file contains all the required Python dependencies for the App. The requirements.txt file is used by the ``tclib`` command to build the **lib_x.x.x** directories.

run.py (required)
~~~~~~~~~~~~~~~~~

Template file that is called by ThreatConnect and ``tcrun`` to launch the App. This file should not be edited and will get updated when using ``tcprofile --action update --template <template name>`` command.

setup.cfg (optional)
~~~~~~~~~~~~~~~~~~~~

This file contains Python configurations data, specifically for linting ignores/excludes.

tcex.d (optional)
~~~~~~~~~~~~~~~~~

This directory is created when creating testing profile using the ``tcprofile`` command.  This directory hold both the staging data and profiles JSON files.

tcex.d/data (optional)
~~~~~~~~~~~~~~~~~~~~~~

This directory contains the JSON staging files.

tcex.d/profiles (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~

This directory contains the JSON profile files.

tcex.json (required)
~~~~~~~~~~~~~~~~~~~~

This is the main TcEx framework configuration file. It required to run local testing and for packaging, but should not be included in the App package.

tcex_json_schema.json (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the JSON schema for the install.json configuration file. If this file is present the ``tcpackage`` command will validate the "install.json" before packaging the App.

.. _app_directory_structure:

-------------------------
App-Directory Structure
-------------------------

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
    └── tcex.json

.gitignore (optional)
~~~~~~~~~~~~~~~~~~~~~

This template file specifies intentionally untracked files that Github should ignore. This file is part of the template update, but it optionally can be updated, if required.

.. literalinclude:: ../../app_init/gitignore
    :language: bash
    :linenos:

.pre-commit-config.yaml (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the configuration file for the ``pre-commit`` Python CLI tool. This configuration is the same one that is used for the internal development of Apps.

.. literalinclude:: ../../app_init/.pre-commit-config.yaml
    :language: yaml
    :linenos:

README.md (required)
~~~~~~~~~~~~~~~~~~~~

The ``README.md`` file should contain any relevant information for the App and the App release notes.

.. literalinclude:: ../../app_init/README.md
    :language: md
    :linenos:

__main__.py (required)
~~~~~~~~~~~~~~~~~~~~~~

This template file should not be modified.

.. literalinclude:: ../../app_init/__main__.py
    :language: python
    :linenos:

app.py (required)
~~~~~~~~~~~~~~~~~

This file contains the "main" App logic and the ``run()`` method that is called by default. It also can contain methods for **tc_actions**.

.. literalinclude:: ../../app_init/playbook/app.py
    :language: python
    :linenos:

args.py (required)
~~~~~~~~~~~~~~~~~~

This file contains the args required for the App to function properly.  Only App args are required to be defined.  The default args are part of the TcEx framework and are added automatically.

.. literalinclude:: ../../app_init/playbook/args.py
    :language: python
    :linenos:

install.json (required)
~~~~~~~~~~~~~~~~~~~~~~~

This is the main configuration file for the App and controls what inputs and outputs will be presented to the user.

.. literalinclude:: ../../app_init/playbook_utility/install.json
    :language: json
    :linenos:

log (temporary)
~~~~~~~~~~~~~~~

This directory is created when running a testing profile locally. All App output is written to this directory, as well as the output from the test cases.

log/app.log (temporary)
~~~~~~~~~~~~~~~~~~~~~~~

This log file contains the logging output of the App.

log/message.tc (temporary)
~~~~~~~~~~~~~~~~~~~~~~~~~~

This file contains the App exit message. The contents of this file will be displayed in the UI when the App is run the in platform. For local testing, the file should be verified to have content on successful App completion and on failure.

log/run.log (temporary)
~~~~~~~~~~~~~~~~~~~~~~~

This log file contains the output from the ``tcrun`` command and will contain information about validation rules.

playbook_app.py (required)
~~~~~~~~~~~~~~~~~~~~~~~~~~

This template file contains base logic for a Playbook App. This file should not be edited and will get updated when using the ``tcinit --action update --template <template name>`` command.

.. literalinclude:: ../../app_init/playbook/playbook_app.py
    :language: python
    :linenos:

pyproject.toml (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~

This is a Python tool configuration file that contains the configuration for the **black** formatting tool used to format all Python code.

.. literalinclude:: ../../app_init/pyproject.toml
    :language: python
    :linenos:

requirements.txt (required)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This file contains all the required Python dependencies for the App. The **requirements.txt** file is used by the ``tclib`` command to build the **lib_x.x.x** directories.

.. literalinclude:: ../../app_init/requirements.txt
    :language: python
    :linenos:

run.py (required)
~~~~~~~~~~~~~~~~~

This template file is called by ThreatConnect to launch the App. This file should not be edited and will get updated when using the ``tcinit --action update --template <template name>`` command.

.. literalinclude:: ../../app_init/playbook/run.py
    :language: python
    :linenos:

setup.cfg (optional)
~~~~~~~~~~~~~~~~~~~~

This file contains Python configurations data, specifically for linting ignores or excludes.

.. literalinclude:: ../../app_init/setup.cfg
    :language: python
    :linenos:

tcex.json (required)
~~~~~~~~~~~~~~~~~~~~

This is the main TcEx framework configuration file. It is required to run local testing and for packaging, but it should not be included in the App package.

.. literalinclude:: ../../app_init/playbook/tcex.json
    :language: json
    :linenos:

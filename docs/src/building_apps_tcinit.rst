.. _building_apps_tcinit:

----------------------------------
Building Apps: Templates (tcinit)
----------------------------------

Summary
-------

The ``tcinit`` CLI tool provides a simple interface to begin a new project from a template and to keep Framework files updated.  There are several templates that support specific-use cases. Most templates are working Apps that can easily be modified to the developer's use case.

Usage
-----

To get the latest usage and template choices for ``tcinit``, run ``tcinit -h``.

.. code:: bash

    usage: tcinit [-h] [--branch {master,develop}]
                  [--action {create,update,migrate}]
                  [--template {external,external_ingress,job,job_batch,playbook,playbook_actions,playbook_utility}]
                  [--force]

    optional arguments:
      -h, --help            Show this help message and exit
      --branch {master,develop}
                            git branch.
      --action {create,update,migrate}
                            (default: create) Choose "create" to initialize a new
                            App, "update" to download updates to App framework
                            files, and "migrate" to update a non App Builder
                            compliant App to use a standard template.
      --template {external,external_ingress,job,job_batch,playbook,playbook_actions,playbook_utility}
                            (default: playbook) Choose an appropriate App template for the current
                            project.
      --force               Enable this flag to forcibly overwrite existing files
                            in the current working directory.

~~~~~~~~~~~~
Common Usage
~~~~~~~~~~~~

To initialize a new App, run this command from the project directory:

.. code:: bash

    tcinit --template playbook_utility

To update an existing App, run the command below from the project directory. The **update** action will download all Frameworks files to ensure that these files are the latest with any bug fixes or updates.  It is best practice to run the **update** action whenever an App is being updated for new features or bug fixes.

.. code:: bash

    tcinit --action update --template playbook

Job App Templates
-----------------

The ``run()`` method is the default method that is called when an App is executed. For simple Apps, the core logic of the App can be written in this method.  For more advanced Apps, additional methods can be added to the **app.py** file, if required.

~~~~~~~~~
Job (job)
~~~~~~~~~

This basic template provides the structure for a Job App without any logic.  This template is intended for advanced users that only require the App structure.

app.py
""""""

.. literalinclude:: ../../app_init/job/app.py
    :language: python
    :linenos:

~~~~~~~~~~~~~~~~~~~~~~~~~
Job Batch (job_batch)
~~~~~~~~~~~~~~~~~~~~~~~~~

This template provides a working example of how to download remote-threat intel (md5 hash Indicators) and write the data in the ThreatConnect platform using the TcEx :ref:`Batch Module <module_batch>`.  The URL is defined in the ``init()`` method for convenience. In the ``run()`` method, the Batch module is instantiated. Next, the data is retrieved from the remote URL and written to the Batch module. Finally, the Batch Job is submitted to ThreatConnect for processing.

app.py
""""""

.. literalinclude:: ../../app_init/job_batch/app.py
    :language: python
    :linenos:

Playbook App Templates
----------------------

~~~~~~~~~~~~~~~~~~~
Playbook (playbook)
~~~~~~~~~~~~~~~~~~~

This template provides the structure for a Playbook App without any logic.  This template is intended for advanced users that only require the App structure.

app.py
""""""

.. literalinclude:: ../../app_init/playbook/app.py
    :language: python
    :linenos:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Playbook Actions (playbook_actions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This template provides a working example of **actions** in a Playbook App. Using the Actions feature, a single Playbook can have multiple actions to perform different operations on the provided data. Python decorators are heavily used in this template to provide a clean interface to process inputs for an App.

.. seealso::

    :py:mod:`~tcex.decorators`
        Inline documentation of App decorators

app.py
""""""

.. literalinclude:: ../../app_init/playbook_actions/app.py
    :language: python
    :linenos:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Playbook Utility (playbook_utility)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This template provides a working example of a utility App that takes an input, analyzes or modifies the data, and writes the results as output.

app.py
""""""

.. literalinclude:: ../../app_init/playbook_utility/app.py
    :language: python
    :linenos:

External App Templates
----------------------

The TcEx Framework provides methods to build an App to run in the ThreatConnect Exchange environment.  However, the TcEx Frameworks also supports writing Apps that run external to the ThreatConnect Exchange environment. Two init params are supported during the initialization of TcEx.  The first option, ``TcEx(config_file='app_config.json)``, takes a JSON file as input for the App configuration file. The second option, ``TcEx(config=app_config_dict)``, takes a dictionary of configuration data.  Either param will load the data and make it accessible via the ``self.args`` namespace.

The ``run()`` method is the default method that is called when an App is executed. For simple Apps, the core logic of the App can be written in this method.  For more advanced Apps, additional methods can be added to the **app.py** file, if required.

.. Important: If not using the template simply initialize the TcEx class by passing either a configuration dictionary or a JSON file containing the configuration data (e.g., tcex = TcEx(config=my_config_dict)).

~~~~~~~~~~~~~~~~~~~
Example Config data
~~~~~~~~~~~~~~~~~~~

.. code:: javascript

    {
      "api_access_id": "API_ACCESS_ID",
      "api_default_org": "API_DEFAULT_ORG",
      "api_secret_key": "API_SECRET_KEY",
      "tc_api_path": "TC_API_PATH",
      "tc_log_level": "debug",
      "tc_log_path": "log",
      "tc_owner": "MyOwner",
      "tc_proxy_host": "TC_PROXY_HOST",
      "tc_proxy_password": "TC_PROXY_PASSWORD",
      "tc_proxy_port": "TC_PROXY_PORT",
      "tc_proxy_tc": false,
      "tc_proxy_username": "TC_PROXY_USERNAME"
    }

In the example above the proxy configuration is only required if using a proxy server in the environment.

~~~~~~~~~~~~~~~~~~~
External (external)
~~~~~~~~~~~~~~~~~~~

This basic template provides the structure for an External App without any logic.  This template is intended for advanced users that only require the App structure.

app.py
""""""

.. literalinclude:: ../../app_init/external/app.py
    :language: python
    :linenos:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
External Ingress (external_ingress)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This template provides a working example of how to download remote-threat intel (md5 hash Indicators) and write the data in the ThreatConnect platform using the TcEx :ref:`Batch Module <module_batch>`.  The URL is defined in the ``init()`` method for convenience. In the ``run()`` method, the Batch module is instantiated. Next, the data is retrieved from the remote URL and written to the Batch module. Finally, the Batch Job is submitted to ThreatConnect for processing.

app.py
""""""

.. literalinclude:: ../../app_init/external_ingress/app.py
    :language: python
    :linenos:

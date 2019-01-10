.. _building_apps_tcinit:

----------------------------------
Building Apps - Templates (tcinit)
----------------------------------

Summary
-------

The ``tcinit`` CLI tool provides a simple interface to kick start a new project from a template and to keep framework files updated.  There are several template that supported specific use cases. Most templates are working Apps that can be easily modified to the developers use case.

Usage
-----

To get the latest usage and template choices for ``tcinit`` run ``tcinit -h``.

.. code:: bash

    usage: tcinit [-h] [--branch {master,develop}]
                  [--action {create,update,migrate}] --template
                  {job,job_batch,playbook,playbook_actions,playbook_utility}
                  [--force]

    optional arguments:
      -h, --help            show this help message and exit
      --branch {master,develop}
                            git branch.
      --action {create,update,migrate}
                            (default: create) Choose "create" to initialize a new
                            App, "update" to download updates to App framework
                            files, and "migrate" to update a non App Builder
                            compliant App to use a standard template.
      --template {job,job_batch,playbook,playbook_actions,playbook_utility}
                            Choose an appropriate App template for the current
                            project.
      --force               Enable this flag to forcibly overwrite existing files
                            in the current working directory.

Common Usage
~~~~~~~~~~~~

To initialize a new App run this command from the project directory.

.. code:: bash

    tcinit --template playbook_utility

To update an existing App run this command from the project directory. The **update** action will download all frameworks files to ensure these files are the latest with any bug fixes or updates.  It is best practice to run the **update** action whenever an App is being updated for new features or bug fixes.

.. code:: bash

    tcinit --action update --template playbook_utility

Job App Templates
-----------------

The ``run()`` method is the default method that is called when an App is executed. For simple Apps the core logic of the App can be written in this method.  For more advanced Apps additional methods can be added to the **app.py** file if required.

Job (job)
~~~~~~~~~

This basic template provides the structure for a Job App without any logic.  This template is intended for advanced users that only require the App structure.

app.py
""""""

.. literalinclude:: ../../app_init/job/app.py
    :language: python
    :linenos:

Job Ingress (job_ingress)
~~~~~~~~~~~~~~~~~~~~~~~~~

This template provides a working example of downloading remote threat intel (md5 hash indicators) and writing the data in the ThreatConnect Platform using the TcEx :ref:`Batch Module <module_batch>`.  The URL is defined in the ``init()`` method for convenience. In the ``run()`` method the batch module is instantiated. Next the data is retrieved from the remote URL and written to the batch module. Finally the batch job is submitted to ThreatConnect for processing.

app.py
""""""

.. literalinclude:: ../../app_init/job_batch/app.py
    :language: python
    :linenos:

Playbook App Templates
----------------------

Playbook (playbook)
~~~~~~~~~~~~~~~~~~~

This template provides the structure for a Playbook App without any logic.  This template is intended for advanced users that only require the App structure.

app.py
""""""

.. literalinclude:: ../../app_init/playbook/app.py
    :language: python
    :linenos:

Playbook Actions (playbook_actions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This template provides a working example of "actions" in a Playbook App. Using the "actions" feature a single Playbook can have multiple actions to perform different operations on the provided data. Python decorators are heavily used in this template to provide a clean interface into processing inputs for an App.

.. seealso::

    :py:mod:`~tcex.tcex_app_decorators`
        Inline documentation of App decorators.

app.py
""""""

.. literalinclude:: ../../app_init/playbook_actions/app.py
    :language: python
    :linenos:

Playbook Utility (playbook_utility)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This template provides a working example of a utility App that takes an input, analyzes or modifies the data, and writes the results as output.

app.py
""""""

.. literalinclude:: ../../app_init/playbook_utility/app.py
    :language: python
    :linenos:

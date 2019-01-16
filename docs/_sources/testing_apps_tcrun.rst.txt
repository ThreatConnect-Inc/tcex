.. _testing_apps_tcrun:

---------------------------------------
Testing Apps - Running Profiles (tcrun)
---------------------------------------

This CLI tool provides a simple interface to run the App locally using the profiles created using the :ref:`tcprofile <testing_apps_tcprofile>` command.  If the profile has validation rules defined the ``tcrun`` command will validate the output variables as defined in the validation rules.

Usage
-----

.. code:: bash

    usage: tcrun [-h] [--config CONFIG] [--docker] [--docker_image DOCKER_IMAGE]
                 [--autoclear] [--halt_on_fail] [--group GROUP]
                 [--logging_level LOGGING_LEVEL] [--profile PROFILE] [--quiet]
                 [--report REPORT] [--truncate TRUNCATE] [--unmask] [--vscd]
                 [--vscd_port VSCD_PORT]

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG       The configuration file. (default: "tcex.json")
      --docker              (Experimental) Run the App in a docker container.
      --docker_image DOCKER_IMAGE
                            (Experimental) Override the docker container defined
                            in install.json or profile.
      --autoclear           Clear Redis data before running.
      --halt_on_fail        Halt on any failure.
      --group GROUP         The group of profiles to run.
      --logging_level LOGGING_LEVEL
                            The logging level.
      --profile PROFILE     The profile to run. (default: "default")
      --quiet               Suppress the output from the App.
      --report REPORT       The JSON report filename.
      --truncate TRUNCATE   (Advanced) The length at which to truncate successful
                            validation data in the logs (default=50).
      --unmask              Unmask masked args.
      --vscd                (Experimental) Enable Visual Studio Code debugging
                            using attach method on port 5678.
      --vscd_port VSCD_PORT
                            (Experimental) Visual Studio Code debugging port
                            (default: 5678).

Common Usage
~~~~~~~~~~~~

The following command will run the "simple-json" profile.

.. code:: bash

    tcrun --profile simple-json

The following command will run all profiles in the "qa-build" group.

.. code:: bash

    tcrun --group qa-build

Results
-------
The ``tcrun`` command outputs a report for all profile run.  This report show whether the execution of the profile passed or failed and if the profile passed it displays the results of the validations rules.


.. code:: bash

    Report:
                                                           Validations
    Profile:                      Execution:               Passed:   Failed:
    simple_data                   Passed                   2         0


Troubleshooting
---------------
All Apps log to the ``app.log`` file in the appropriate log directory.  Any errors during execution of the App will be displayed there.  The ``tcrun`` command logs to the ``run.log``  in the same log directory. This log file is structure to help quickly identify problems with validations.  Any failed validation will be logged at **ERROR** level.

Exit Codes
----------
The ``tcrun`` command can validate the exit code of the App.  This allows for setting up fail scenarios profiles.  All Apps should exit with a valid exit code and handle failures gracefully.  Using the exit_codes parameter you can provide "bad" data to the App and ensure it exits with the proper exit code.

.. code-block:: javascript

  "exit_codes": [1]

.. note:: For Runtime/Job Apps (non Playbook Apps) valid exit codes are 0, 1, and 3.  For certain profiles you may expect an exit code of 0 for success or 3 for partial success/partial failure.  This can be achieved by adding both status codes to the **exit_codes** parameter array.

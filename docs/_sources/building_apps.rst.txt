.. include:: <isonum.txt>
.. _building_apps:

=============
Building Apps
=============

The ThreatConnect |trade| TcEx Framework provides multiple scripts to assist in testing and building apps locally.  The TcEx Framework ships with the Python scripts ``tclib``, ``tcrun``, and ``tcpackage`` which after installation will be available as CLI commands.

The ``__main__.py`` file provided with the TcEx framework should be copied to your App base directory.  This script will be called when the ThreatConnect Platform executes the App.

Build Local Modules
===================
Running ``tclib`` will download/install all required Python dependencies defined in the Apps requirements.txt file to a local ``lib_<version>`` directory.

.. note:: Typically calling ``tclib`` with no arguments is the most common use case.  If building an App for distribution using a configuration file to define the lib structure is preferable.

.. code:: bash

    usage: tclib [-h] [--app_name APP_NAME] [--app_path APP_PATH]
                 [--config CONFIG]

    optional arguments:
      -h, --help           show this help message and exit
      --app_name APP_NAME  Fully qualified path of App.
      --app_path APP_PATH  Fully qualified path of App.
      --config CONFIG      Configuration file for gen lib.

Packaging an App
================
Running ``tcpackage`` will build a zip package of your App that can be installed directly in the ThreatConnect Platform.  For Apps packages that contain multiple Apps using separate **install.json** files add the ``--bundle`` argument to build a bundle.  When using multiple **install.json** files the prefix of the filename is the App name (e.g. MyApp.install.json will have an App name of **MyApp**).  During the build process validation of the **install.json** file will happen automatically if the **tcex_json_schema.json** is included in the base directory of your App.

.. Note:: Typically the only This method only builds the Python dependencies for the version of Python that is used to run the ``./app.py`` script. To build for multiple versions of Python the ``./app.py --package`` must be run multiple times for each supported Python version (e.g 2.7.12, 3.4.5, 3.5.2, 3.6.0).  Building the App for all required Python versions is possible using an external tool like Maven.

.. code:: bash

    usage: tcpackage [-h] [--bundle] [--exclude EXCLUDE] [--config CONFIG]
                     [--dryrun] [--install_json INSTALL_JSON] [--outdir OUTDIR]
                     [--validate VALIDATE]

    optional arguments:
      -h, --help            show this help message and exit
      --bundle              Build a bundle file.
      --exclude EXCLUDE     File and directories to exclude from build.
      --config CONFIG       Build configuration file.
      --install_json INSTALL_JSON
                            The install.json file name for the App that should be
                            built.
      --outdir OUTDIR       Location to write the outfile.

Testing App Locally
===================
Apps are called from the ThreatConnect Platform using Command Line Interface Arguments or CLI Args.  To simulate being called from ThreatConnect the TcEx ``tcrun`` script provides a method for converting a JSON file to CLI Args.  Running ``tcrun`` will read the ``tcex.json`` file and parse the **default** profile.  To specify a different file the ``--config`` argument can be passed (e.g. ``--config my_config.json``).  To run a specific profile the ``--profile`` argument can be passed (``--profile add-indicator``).  A group of commands can also be run using the ``--group`` argument (e.g. ``--group use-sample-data``).

.. code:: bash

    usage: tcrun [-h] [--config CONFIG] [--halt_on_fail] [--group GROUP]
                 [--profile PROFILE] [--quiet] [--unmask]

    optional arguments:
      -h, --help         show this help message and exit
      --config CONFIG    The configuration file. (default: "tcex.json")
      --halt_on_fail     Halt on any failure.
      --group GROUP      The group of profiles to executed.
      --profile PROFILE  The profile to be executed. (default: "default")
      --quiet            Suppress output.
      --unmask           Unmask masked args.

tcex.json Format
----------------

.. note:: To help protect credentials in the **tcex.json** file environment variables can be used in the file.  In order to use environemnt variables prefix the variable with `$env` or `$envs` to mask the value in the output from ``tcrun``.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
      "profiles": [{
        "args": {
          "api_access_id": "1234567890",
          "api_secret_key": "abcdefghijklmnopqrstuvwxyz0987654321",
          "logging": "debug",
          "message": "#App:1234:slack-string!String",
          "slack_api_token": "01234abcde",
          "slack_recipient": "@bob",
          "tc_api_path": "https://api.threatconnect.com",
          "tc_log_path": "log",
          "tc_log_to_api": true,
          "tc_out_path": "log",
          "tc_playbook_db_type": "Redis",
          "tc_playbook_db_context": "7960ab08-26cb-4140-abb9-9310bb45ac86",
          "tc_playbook_db_path": "localhost",
          "tc_playbook_db_port": "6379",
          "tc_proxy_host": "10.10.10.10",
          "tc_proxy_port": "3128",
          "tc_proxy_external": true,
          "tc_proxy_tc": true,
          "tc_temp_path": "log"
        },
        "group": "full-functionality",
        "quiet": false,
        "profile_name": "send-slack-message",
        "script": "slack"
      }]
    }

.. Note:: The **args** section should contain all the CLI Args your app requires to run. The **group** section defines which group this profile should run under and the **profile_name** is the name which can be used to run the profile.  The **script** field is the name of the actual Python script to run minus the **.py** extension.  The **quiet** field indicates whether the app should print output.

Staging Redis Data
------------------

.. Important:: A local instance of Redis must be running to test locally.

In order to test using variable inputs the data can be manually added to Redis.  The ``tcrun`` command has functionality to "stage" the data in redis that can be used to simulate an upstream App writing data to Redis.  This staged data can be and added a single json file or multiple reusable files.  Once the files have been created they should be referenced in the Profile.


.. code-block:: javascript

    [{
      "args": {
        "api_access_id": "$env.API_ACCESS_ID",
        "api_secret_key": "$envs.API_SECRET_KEY",
        "logging": "debug",
        "entity": "#App:0023:indicator-associations!TCEntityArray",
        "tag": "QaTagCreate",
        "tc_api_path": "$env.TC_API_PATH",
        "tc_log_path": "log",
        "tc_log_to_api": true,
        "tc_out_path": "log",
        "tc_temp_path": "log",
        "tc_playbook_db_type": "Redis",
        "tc_playbook_db_context": "1860ab08-26cb-4140-abb9-9310bb45ac86",
        "tc_playbook_db_path": "localhost",
        "tc_playbook_db_port": "6379",
        "tc_playbook_out_variables": "#App:0072:tc.tag.fail_count!String,#App:0072:tc.tag.success_count!String,#App:0072:tc.tag.tags!StringArray"
      },
      "data_files": [
        "tcex.d/data/indicator-associations.json"
      ],
      "description": "Pass test of create tag.",
      "group": "qa-build",
      "profile_name": "tag-create-indicator",
      "quiet": false,
      "script": "tc_tag",
    }]


Data Validation
---------------

Coming Soon


Exit Codes
----------

Coming Soon
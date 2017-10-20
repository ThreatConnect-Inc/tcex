.. _building_apps_testing:

Apps are called from the ThreatConnect Platform using Command Line Interface Arguments or CLI Args.  To simulate being called from ThreatConnect the TcEx ``tcrun`` command provides a method for converting a defined JSON structure to CLI Args.  Running ``tcrun`` will read the ``tcex.json`` file and parse the **args** section from the **default** profile in the ``profiles`` parameter array.  To specify a different file the ``--config`` argument can be passed (e.g. ``--config my_config.json``).  To run a specific profile the ``--profile`` argument can be passed (``--profile add-indicator``).  A group of profiles can also be run using the ``--group`` argument (e.g. ``--group run-all``).

.. Note:: When testing a single profile (use case) the ``tcrun`` command would be called using that profile.  Before packaging the App calling ``tcrun`` using a group that will run multiple profiles is typical.

Usage
-----

.. code:: bash

    usage: tcrun [-h] [--config CONFIG] [--halt_on_fail] [--group GROUP]
                 [--profile PROFILE] [--quiet] [--unmask]

    optional arguments:
      -h, --help         show this help message and exit
      --config CONFIG    The configuration file. (default: tcex.json)
      --halt_on_fail     Halt on any failure.
      --group GROUP      The group of profiles to executed.
      --profile PROFILE  The profile to be executed. (default: "default")
      --quiet            Suppress output.
      --unmask           Unmask masked args.

Profile Format
----------------
Multiple testing profiles can be defined in the **tcex.json** to help testing coverage.  Each profile should include a unique **profile_name** and a group which allows for running multiple profiles at once.

.. note:: The ``tcrun`` command provides a feature that allow using environment variables in the **tcex.json** configuration file.  By prefixing the environment variable with **$env.** or **$envs.** the ``tcrun`` command will pull the value from the OS Environment variable. This feature helps facilitate quickly changing values between testing environments and/or user credentials.

.. important:: To protect credentials in the **tcex.json** configuration file the **$envs.** feature should be used.  This will keep the credentials out of version control and will mask them on command output.  To unmask the credentials temporarily the ``--unmask`` command can be passed to ``tcrun``.

.. code:: javascript

    {
      "profiles": [{
        "args": {
          "api_access_id": "$env.TC_ACCESS_ID",
          "api_secret_key": "$envs.TC_SECRET_KEY",
          "logging": "debug",
          "tc_api_path": "$env.TC_API_PATH",
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
          "tc_temp_path": "log",
          "message": "#App:1234:slack-string!String",
          "slack_api_token": "$envs.SLACK_API_TOKEN",
          "slack_recipient": "@bob"
        },
        "groups": ["run-all"],
        "install_json": "install.json",
        "quiet": false,
        "profile_name": "send-slack-message"
      }]
    }

.. Note:: The **args** section should contain all the CLI Args your app requires to run. The **groups** section defines which groups this profile should run under and the **profile_name** is the name which can be used to run the profile.  The **quiet** field indicates whether the app should print output.

Profile Creation
----------------
The TcEx framework provides the ``tcprofile`` command to automatically generate a profile from the install.json file.  The output of the ``tcprofile`` command will set the exit_code to 0 by default, however testing failure scenarios is also possible by setting the exit code to 1. Some default values will be added to the args section, but any custom inputs will need to be populated with the appropriate data.

For playbook Apps the ``tcprofile`` command will also create 2 standard validations for each output variable.  The first validation will check to see if the output variable is **null** and the second will ensure the output variables is the correct type.

.. note:: The ``tcprofile`` command can be run multiple times to generate several different profiles with different input and/or output variables.

.. code-block:: bash

    usage: tcprofile [-h] [--config CONFIG] [--outfile OUTFILE]

    optional arguments:
      -h, --help         show this help message and exit
      --config CONFIG    The install.json file name. (default: "install.json")
      --outfile OUTFILE  File to output or append profile.

Staging Redis Data
------------------

.. Important:: A local instance of Redis must be running to test locally.

In order to test using variable inputs the data can be manually added to Redis.  The ``tcrun`` command has functionality to "stage" the data in redis that can be used to simulate an upstream App writing data to Redis.  This staged data can be and added to a single json file or multiple reusable files.  Once the files have been created they should be referenced in the Profile.

Example Data File
-----------------

.. note:: Data files can contain a single data input or multiple data inputs.  In most cases it better to have separate files so the data can be reused in multiple Profiles.

.. code-block:: javascript

    [{
      "data": [{
          "id": 125,
          "value": "threat001-build-testing",
          "type": "Threat",
          "ownerName": "qa-build",
          "dateAdded": "2017-08-16T18:45:42-04:00",
          "webLink": "https://mytc.myorg.com/auth/threat/threat.xhtml?threat=125"
        },
        {
          "id": 124,
          "value": "incident001-build-testing",
          "type": "Incident",
          "ownerName": "qa-build",
          "dateAdded": "2017-08-16T18:44:57-04:00",
          "webLink": "https://mytc.myorg.com/auth/incident/incident.xhtml?incident=124"
        },
        {
          "id": 123,
          "value": "doc001-build-testing",
          "type": "Document",
          "ownerName": "qa-build",
          "dateAdded": "2017-08-16T18:43:54-04:00",
          "webLink": "https://mytc.myorg.com/auth/document/document.xhtml?document=123"
        },
        {
          "id": 122,
          "value": "camp001-build-testing",
          "type": "Campaign",
          "ownerName": "qa-build",
          "dateAdded": "2017-08-16T18:40:56-04:00",
          "webLink": "https://mytc.myorg.com/auth/campaign/campaign.xhtml?campaign=122"
        },
        {
          "id": 116,
          "value": "adver001-build-testing",
          "type": "Adversary",
          "ownerName": "qa-build",
          "dateAdded": "2017-08-16T18:35:07-04:00",
          "webLink": "https://mytc.myorg.com/auth/adversary/adversary.xhtml?adversary=116"
        }
      ],
      "variable": "#App:0022:groups!TCEntityArray"
    }]

Profile with Data File
----------------------

.. code-block:: javascript

    [{
      "args": {
        "api_access_id": "$env.API_ACCESS_ID",
        "api_secret_key": "$envs.API_SECRET_KEY",
        "logging": "debug",
        "tc_api_path": "$env.TC_API_PATH",
        "tc_log_path": "log",
        "tc_log_to_api": true,
        "tc_out_path": "log",
        "tc_temp_path": "log",
        "tc_playbook_db_type": "Redis",
        "tc_playbook_db_context": "1860ab08-26cb-4140-abb9-9310bb45ac86",
        "tc_playbook_db_path": "localhost",
        "tc_playbook_db_port": "6379",
        "tc_playbook_out_variables": "#App:0072:tc.tag.fail_count!String,#App:0072:tc.tag.success_count!String,#App:0072:tc.tag.tags!StringArray",
        "entity": "#App:0022:groups!TCEntityArray",
        "tag": "QaTagCreate"
      },
      "data_files": [
        "tcex.d/data/groups.json"
      ],
      "description": "Pass test of create tag.",
      "group": "qa-build",
      "profile_name": "create-tag-on-groups",
      "quiet": false,
      "script": "tc_tag",
    }]


Data Validation
---------------
The ``tcrun`` command provides some basic data validation for output variables.  By defining the **validations** parameter array in the **tcex.json** file the ``tcrun`` command will pull the values from the REDIS DB and perform the provided operator on the data. This action simulates a downstream App reading the data from REDIS.

**Example Configuration**

.. code-block:: javascript

    "validations": [{
        "data": null,
        "operator": "ne",
        "variable": "#App:1073:tc.association.success_count!String"
      },
      {
        "data": "string",
        "operator": "it",
        "variable": "#App:1073:tc.association.success_count!String"
      },
      {
        "data": null,
        "operator": "ne",
        "variable": "#App:1073:tc.association.fail_count!String"
      },
      {
        "data": "string",
        "operator": "it",
        "variable": "#App:1073:tc.association.fail_count!String"
      }
    ]

**Supported Operators**

.. code-block:: python

        'eq' # equal to
        'ew' # ends with
        'ge' # greater than or equal to
        'gt' # greater than
        'in' # in array
        'ni' # not in array
        'it' # is type (array, binary, entity, string)
        'lt' # less than
        'le' # less than or equal to
        'ne' # not equal
        'sw' # start with


Exit Codes
----------
The ``tcrun`` command can validate the exit code of the App.  This allows for setting up fail scenarios profiles.  All Apps should exit with a valid exit code and handle failures gracefully.  Using the exit_codes parameter you can provide "bad" data to the App and ensure it exits with the proper exit code.

.. code-block:: javascript

  "exit_codes": [1]

.. note:: For Custom Apps (non Playbook Apps) valid exit codes are 0, 1, and 3.  For certain profiles you may expect an exit code of 0 for success or 3 for partial success/partial failure.  This can be achieved by adding both status codes to the **exit_codes** parameter array.
.. _testing_apps_tcprofile:

-----------------------------------
Testing Apps - Profiles (tcprofile)
-----------------------------------

The ``tcprofile`` CLI tool provides a simple interface to create testing profiles.  These profiles can be used to perform local testing of the App before deploying to ThreatConnect.  Multiple profiles can be create and grouped to allow testing of different data inputs and outputs.

By default the ``tcprofile`` command will add any default values defined in the **install.json** file to the args value.  Args without a default value will have to populated manually. For validation rules there are 2 rules created automatically for each output variables.  One rule ensures that the output variable is not null and should be update to a more specific test. The second rule validates that the output variables is of the correct type (e.g., String value is a <str> type, StringArray value is of <list> type.).

.. Important:: The generation of profiles uses the **install.json** file to create the ``args.apps`` section and the ``validation`` section of the profile. It is important that all inputs and outputs are defined in the **install.json** prior to running the ``tcprofile`` command.

.. Important:: A local instance of Redis must be running to test Playbook Apps locally.

Usage
-----

.. code:: bash

    usage: tcprofile [-h]
                     [--action {create,delete,replace_validation,update,validate}]
                     [--ij IJ] [--outdir OUTDIR] [--outfile OUTFILE]
                     [--profile_name PROFILE_NAME] [--redis_host REDIS_HOST]
                     [--redis_port REDIS_PORT] [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --action {create,delete,replace_validation,update,validate}
      --ij IJ               (Advanced) The install.json file name (default:
                            install.json).
      --outdir OUTDIR       (Advanced) The *base* output directory containing the
                            data/profiles folder(default: tcex.d).
      --outfile OUTFILE     (Advanced) The filename for the profile (default:
                            <profile name>.json).
      --name PROFILE_NAME   The profile name to create, delete, or
                            replace_validation.
      --redis_host REDIS_HOST
                            (Advanced) The redis host.
      --redis_port REDIS_PORT
                            (Advanced) The redis port.
      --verbose             Show verbose output.

Common Usage
~~~~~~~~~~~~

To create a new profile run the following command.  The profile will be created in the **tcex.d/profiles** directory of the project.

.. code:: bash

    tcprofile --name simple_data

.. note:: The ``tcprofile`` command can be run multiple times to generate several different profiles with different input and/or output variables.

Output
~~~~~~

After running the ``tcprofile`` a the directory **tcex.d** will be created in the project directory.  The **tcex.d** directory will have the structure displayed below. New testing profiles can be added to existing file or new files can be created.

.. code:: bash

    tcex.d
    ├── data
    └── profiles
        └── simple_data.json

Updates
~~~~~~~

Once a profile has been created, testing value needs to be added to the JSON data.  All inputs in the ``args.apps`` section need to have values set or updated. A description can be added to define the intent of the testing profile.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

An important part of local testing is setting up the appropriate environmental variables.  In each profile the ``args.default`` section has all the default args that will be provided to every App by the ThreatConnect Platform during execution. The values for these args can be entered directly into the configuration file, however to keep sensitive data out of VCS systems the use of environment variables is employed.

.. NOTE:: This list of environment variables can be found by running ``tcprofile -h``.

Update the values for each variable and add to the local environment (e.g., ~/.bashrc or ~/.bash_profile). Once done the environment file will need to be sourced once or the shell restarted before the values are available (e.g., source ~/.bashrc).

.. code:: bash

    # ThreatConnect API Credential and URL
    export API_DEFAULT_ORG=MyOrg
    export API_ACCESS_ID=1234
    export API_SECRET_KEY=abc123
    export TC_API_PATH=https://maclaren.pub/api

    # API Token can be supplied optionally, but must be updated frequently.
    export TC_TOKEN=123-abc-456-def

    # Proxy settings are optional
    export TC_PROXY_HOST=10.10.10.10
    export TC_PROXY_PORT=3128
    export TC_PROXY_USERNAME=robin
    export TC_PROXY_PASSWORD=sparkles

    # The Redis IP/Host and Port
    export DB_PATH=localhost
    export DB_PORT=6379

.. IMPORTANT:: To test that the values are available run ``echo $API_ACCESS_ID``.

Profile Format
--------------
Multiple testing profiles can be created in the **tcex.d/profiles** directory to increase testing coverage.  Each profile must include a unique **profile_name**. One or more groups can be added to a profile to allow testing of multiple profiles at once.

.. code:: javascript

    [
      {
        "args": {
          "app": {
            "indent": "4",
            "json_data": "{\"four\": 5, \"one\": 1, \"two\": 2, \"three\": 3}",
            "sort_keys": true
          },
          "default": {
            "api_access_id": "$env.API_ACCESS_ID",
            "api_default_org": "$env.API_DEFAULT_ORG",
            "api_secret_key": "$envs.API_SECRET_KEY",
            "tc_api_path": "$env.TC_API_PATH",
            "tc_docker": false,
            "tc_in_path": "log",
            "tc_log_level": "debug",
            "tc_log_path": "log",
            "tc_log_to_api": false,
            "tc_out_path": "log",
            "tc_playbook_db_context": "c723fe88-d4bb-40db-8a98-bdec323e6190",
            "tc_playbook_db_path": "$env.DB_PATH",
            "tc_playbook_db_port": "$env.DB_PORT",
            "tc_playbook_db_type": "Redis",
            "tc_playbook_out_variables": "#App:7909:json.pretty!String",
            "tc_proxy_external": false,
            "tc_proxy_host": "$env.TC_PROXY_HOST",
            "tc_proxy_password": "$envs.TC_PROXY_PASSWORD",
            "tc_proxy_port": "$env.TC_PROXY_PORT",
            "tc_proxy_tc": false,
            "tc_proxy_username": "$env.TC_PROXY_USERNAME",
            "tc_temp_path": "log"
          }
        },
        "autoclear": true,
        "clear": [],
        "data_files": [],
        "description": "",
        "exit_codes": [
          0
        ],
        "groups": [
          "qa-build"
        ],
        "install_json": "install.json",
        "profile_name": "simple_data",
        "quiet": false,
        "validations": [
          {
            "data": {
              "four": 4,
              "one": 1,
              "three": 3,
              "two": 2
            },
            "data_type": "redis",
            "operator": "json-compare",
            "variable": "#App:7909:json.pretty!String"
          },
          {
            "data": "string",
            "data_type": "redis",
            "operator": "it",
            "variable": "#App:7909:json.pretty!String"
          }
        ]
      }
    ]

args.app
~~~~~~~~

The ``args.app`` section of the profile contains all the CLI Args from the ``params`` section of the **install.json** file.

args.default
~~~~~~~~~~~~

The ``args.default`` section has all the default args that are passed to all Apps by ThreatConnect. Some of these args are in the format ``$env.<value>`` or ``$envs.<value>``. Args in this format reference environment variables defined on the local workstation. These environment variables must be created manually by the developer.  The ``$envs.<values>`` are used to represent sensitive data, such as API credentials and will be masked when printed to the screen.

autoclear
~~~~~~~~~

The ``autoclear`` boolean field enables clearing of Redis and/or ThreatConnect data when set to **true**. By using autoclear the developer can assure that validation rules are not using stale data. The most common use case is to leave this enabled unless using output data from previous profiles.

data_files
~~~~~~~~~~

The ``data_files`` section of the configuration allow an array of staging files to be defined. Each staging file defined in this section will be staged to Redis and/or ThreatConnect to simulate an upstream App.  For help creating staging files see the `Data Files`_ section.

description
~~~~~~~~~~~

The ``description`` field allows for a helpful message that will be logged when the profile is run (e.g., "Pass test of simple JSON data." or "Fail test when passing in null data.").

exit_codes
~~~~~~~~~~

The ``exit_codes`` section allows for one or more exit codes to be defined. If the exit code of the App matches one of the defined values then the profile was completed successfully. For "fail" testing adding an exit code of **1** is appropriate.  If the App exits with a **1** then the profile succeeded.

.. NOTE:: For Job Apps there are 3 valid exit codes.  An exit code of 0 indicates success, 1 indicates failure, and 3 indicates partial success/failure.

groups
~~~~~~

The ``groups`` section allows for one or more group names so that the profile can be run grouped with other profiles.

install_json
~~~~~~~~~~~~

The ``install_json`` field defines the install.json filename of the App. This is typically ``install.json`` unless working in a Multi-App bundle.

profile_name
~~~~~~~~~~~~

The ``profile_name`` field defines the name of the profile.  This is the name that will be used to run the profile using the ``tcrun`` command.

quiet
~~~~~

The ``quiet`` boolean field will silence all App output when set to **true**.

validations
~~~~~~~~~~~

The ``validations`` section of the configuration file defines validations rules for testing Playbook App outputs.

Staging Redis Data
------------------

In order to test using variable inputs the data can be manually added to Redis.  The ``tcrun`` command has functionality to "stage" the data in redis that can be used to simulate an upstream App writing data to Redis.  This staged data can be and added to a single json file or multiple reusable files.  Once the files have been created they should be referenced in the Profile.

Data Files
----------

.. note:: Data files can contain a single data input or multiple data inputs.  If the data is reusable it is best practice to keep the data in a file by itself so that it can be used in multiple profiles.

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

Data Validation
---------------

The ``tcrun`` command will run any validation rules defined in the profile. Currently the ``tcrun`` command can validate the output data store in Redis by the App.

**Example Configuration**

.. code-block:: javascript

    "validations": [
      {
        "data": {
          "four": 4,
          "one": 1,
          "three": 3,
          "two": 2
        },
        "data_type": "redis",
        "operator": "json-compare",
        "variable": "#App:7909:json.pretty!String"
      },
      {
        "data": "string",
        "data_type": "redis",
        "operator": "it",
        "variable": "#App:7909:json.pretty!String"
      }
    ]

Supported Operators
~~~~~~~~~~~~~~~~~~~

For a list of supported **operator** see the :py:meth:`~bin.tcrun.TcRun.operators` property of the ``tcrun`` command.

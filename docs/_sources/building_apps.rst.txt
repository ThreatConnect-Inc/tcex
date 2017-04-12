.. include:: <isonum.txt>
.. _building_apps:

=============
Building Apps
=============

The ThreatConnect |trade| TcEx Framework provides the :py:mod:`~tcex.tcex_local.TcExLocal` module which includes functionality for testing and building apps locally.  The TcEx Framework ships with the Python script ``app.py`` which can be copied to the base of you App for an easy interface to the TcExLocal module.

The ``__main__.py`` file provided with the TcEx framework should also be copied to your App base directory.  This script will be called when the ThreatConnect Platform executes the App.

Build Local Modules
===================
Running ``./app.py --lib`` will download/install all required Python dependencies defined in the App setup.py file to a local ``lib_<version>`` directory.

Packaging an App
================
Running ``./app.py --package`` will build a zip package of your App that can be installed directly in the ThreatConnect Platform.  For Apps packages that contain multiple Apps using separate **install.json** files add the ``--collection`` argument to build a collection.  An optional argument of ``--zip_out`` can be used to specify where the zip files is written.

.. Note:: This method only builds the Python dependencies for the version of Python that is used to run the ``./app.py`` script. To build for multiple versions of Python the ``./app.py --package`` must be run multiple times for each supported Python version (e.g 2.7.12, 3.4.5, 3.5.2, 3.6.0).  Building the App for all required Python versions is possible using an external tool like Maven.

Validate install.json
=====================
This :ref:`install_json` file defines the properties and inputs of the App.  Running ``./app.py --validate`` will validate the install.json file to ensure basic syntax and format.  If validating an install.json in a collection the ``--install_json`` argument can be passed with the name of the file to be validated.

Testing App Locally
===================
Apps are called from the ThreatConnect Platform using Command Line Interface Arguments or CLI Args.  To simulate being called from ThreatConnect the TcExLocal module provides a method for converting a JSON file to CLI Args.  Running ``./app.py --run`` will read the ``tcex.json`` file and parse the **default** profile.  To specify a different file the ``--config`` argument can be passed (e.g. ``--config my_config.json``).  To run a specific profile the ``--profile`` argument can be passed (``--profile add-indicator``).  A group of commands can also be run using the ``--group`` argument (e.g. ``--group use-sample-data``).

tcex.json Format
----------------

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

In order to test using variable inputs the data must be manually added to Redis.  The code below will simulate an upstream App writing data to Redis.  This code can be saved to a script ``redis-create.py`` and added to the ``tcex.json`` as a profile.  By doing this the local Testing enviroment can be simulate a piece of a running playbook.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    """ standard """
    import os
    """ third party """
    """ custom """
    from tcex import TcEx
    tcex = TcEx()


    def main():
        """ """

        # String variable
        variable = '#App:1234:a-string!String'
        data = 'a-string'
        tcex.playbook.create(variable, data)

        # String Array
        variable = '#App:1234:a-string-array!StringArray'
        data = ['a', 'string', 'array']
        tcex.playbook.create(variable, data)


    if __name__ == "__main__":
        main()
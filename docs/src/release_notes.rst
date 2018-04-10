.. _release_notes:

Release Notes
#############

0.7.x
=====

0.7.18
------
+ Updated jobs module to not call safetag method when using resource module.
+ Updated Intrusion Set class in resource module.
+ Updated group list to include new group types.
+ Added `upload()` and `download()` methods to Report class in resource module.
+ Added Task as a group type.
+ Added new secure params feature.

0.7.17
------
+ Update utils module for handling naive datetime in Py2.
+ Added to_bool() method back to utils module.

0.7.16
------
+ Updated utils datetime methods to not require a timezone.
+ Updated Tag class to urlencode tag value so slashes are supported.
+ Updated safetag method to strip **^** from tag values.
+ Changed modules dependency to use latest version instead of restricting to current version.
+ Added Event, Intrusion Set and Report group types in preparation for TC > 5.6.0.
+ Added metrics module to create and add metrics to ThreatConnect.
+ Added **deleted** endpoint for indicators.

0.7.15
------
+ Updated jobs module to delete by name when using replace for groups.
+ Updated token renewal to log more information on failure.
+ Updated playbooks read binary array to better handle null values.

0.7.14
------
+ Updated file indicator class for proper handling of attributes, tag, and labels.
+ Updated :py:meth:`~tcex.tcex.TcEx.expand_indicators` method to use a new regex to handle more formats for file hashes and custom indicators.

0.7.13
------
+ Fixed issue with embedded variable matching during exact variable check.

0.7.12
------
+ Updated :py:mod:`~tcex.tcex_resources.Resource` for py2 unicode issue in ipaddress module.

0.7.11
------
+ Updated :py:mod:`~tcex.tcex_resources.Resource` module to automatically handle files hashes in format "md5 : sha1 : sha256".
+ Updated :py:mod:`~tcex.tcex_resources.Resource` module to reformat ipv6 addresses to same format as TC.


0.7.10
------
+ Updated **__main__.py** template with better logic to detect Python lib directory version.
+ Updates to regex patterns for variable matching in playbook module.
+ Cleanup of playbook module in handling variables.

0.7.9
-----
+ Major update to :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to better support embedded variables.
+ Add **--report** arg to ``tcrun`` to output a JSON report of profiles and run data.
+ Added new JSON string comparison operator (jc/json compare) to ``tcdata`` to compare two json string (requires deepdiff to be installed locally).

0.7.8
-----
+ Added KeyValueArray operator to ``tcdata`` which allow searching for a single key/value entry in array.
+ Update functionality to replace non-quoted embedded variable to handle duplicate variables in KeyValueArray.

0.7.7
-----
+ Added new string comparison operator (sc) to ``tcdata`` that strips all white space before eq comparison.
+ Added new functionality to :py:mod:`~tcex.tcex_playbook.TcExPlaybook` to replace non-quoted embedded variables in Read KeyValueArrays.
+ Updated Create KeyValue/KeyValueArray methods to not JSON load when passed a String.
+ Added :py:meth:`~tcex.tcex_utils.TcExUtils.any_to_datetime` method to return datetime.datetime object.
+ Added :py:meth:`~tcex.tcex_utils.TcExUtils.timedelta` method to return delta object from two provided datetime expressions.

0.7.6
-----
+ Fixed issue with _newstr_ and dynamic class generation.

0.7.5
-----
+ Updated all TcEx framework CLI commands to use utf-8 encoding by default.
+ Replaced usage of unicode with built-ins str (Python 2/3 compatible.
+ Replaced usage of long with built-ins int (Python 2/3 compatible).
+ Update used of urllib.quote to be Python 2/3 compatible.

0.7.4
-----
+ Updated :py:meth:`~tcex.tcex_resources.Resource.association_custom` to handle boolean values that are passed as strings.
+ Updated :py:meth:`~tcex.tcex.TcEx._resource` method to handle boolean returned as strings from the API.
+ Updated ``tcdata`` to properly delete indicators when using ``--clear`` arg.
+ Update the log module to use **tcex** instead of **tcapp**.

0.7.3
-----
+ Added :py:mod:`~tcex.tcex_utils.TcExUtils` module with date functions to handle common date use cases.
+ Added DeepDiff functionality to ``tcdata`` for validating unsorted dictionaries and list.
+ Updated ``tcdata`` to pull item from lists by index for easier comparison.
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read` method to allow disabling of automatically resolving embedded variables.
+ Updated :py:meth:`~tcex.tcex_resources.Resource.association_custom` method to support file actions.
+ Updated :py:meth:`~tcex.tcex_resources.File.file_action` method as alias to :py:meth:`~tcex.tcex_resources.Resource.association_custom`.

0.7.2
-----
+ Updated ``tcdata`` command for issue on sorting list in Python 3.
+ Added update for tcex.json file to allow the App Version to be specified instead of using programVersion from install.json.

0.7.1
-----
+ Added stub support for associatedGroup in Batch Indicator JSON.
+ Updated the TcEx Job module to better handle Document uploads in Python 3.
+ Updated TcEx Resource module to support query parameter list in the add_payload() method.
+ Updated TcEx Request module to support query parameter list in the add_payload() method.
+ Updated ``tclib`` to remove the old lib directory before creating the lib directory.

0.7.0
-----
+ Updated the TcEx framework to only build custom indicator classes when working with custom indicators.
+ Updated TcJobs module group add logic to fix issue with skipping existing groups.
+ Updated TcJobs module to handle associatedGroup passed as string or int when using **/v2**.

.. Important:: Breaking change to any App that uses the Direct Access method with a Custom Indicator type.

0.6.x
=====

0.6.3
-----
+ Fixed issue in ``tcdata`` when validating data is a not string type.
+ Updated ``tcprofile`` to set type check to binary on Binary data.

0.6.2
-----
+ Updated playbook create_binary and create_binary array for to better support Py3.
+ Update ``tcdata`` to support Security Labels in staged data.
+ Update ``tcdata`` to support adding Associations.
+ Update ``tcdata`` to support variable reference **#App:4768:tc.address!TCEntity::value** during validation.

0.6.1
-----
+ Updated ``tcdata`` to validate String as string_types for "is type" check using six module.
+ Added fix for code font not matching line numbers in the docs.

0.6.0
-----
+ Added :py:mod:`~tcex.tcex_resources.CustomMetric` module to :py:mod:`~tcex.tcex_resources.Resource` module.
+ Renamed ``_args`` variable in tcex.py to ``default_args``.
+ Renamed ``_parser`` variable in tcex.py to ``parser``.
+ Code cleanup (removing any Python 2.5 specific code).

0.5.x
=====

0.5.23
------
+ Replace use of ``str()`` in TcEx playbook module.
+ Updated ``tcrun`` to pass data_owner for each action on ``tcdata``.
+ Updated ``tcdata`` to stage TC data via ``/v2`` instead of batch.
+ Updated ``tcdata`` write Entity out as variable.

0.5.22
------
+ Updated ``tcprofile`` to support new parameters.
+ Updated ``tcdata`` to properly handle older tcex.json files.
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method handle unicode error.
+ Added additional logging to TcEx Job for logging API response.

0.5.21
------
+ Added :py:meth:`~tcex.tcex.TcEx.job` association feature to handle group->indicator and group->group associations.
+ Added :py:meth:`~tcex.tcex.TcEx.safe_group_name` method to ensure group meet the required length.
+ Added ``tcdata`` initial feature to stage Groups and Indicators in ThreatConnect.
+ Updated ``tcrun`` to use new parameter for logging.
+ Updated :py:meth:`~tcex.tcex.TcEx.job` to support upload of file to Document group.

0.5.20
------
+ Updated token renewal URL.
+ Updated ``tcprofile`` to include api_default_org, tc_proxy_external, tc_proxy_host, tc_proxy_port, tcp_proxy_password, tc_proxy_tc, tc_proxy_username.
+ Updated ``tcprofile`` changing tc_playbook_db_path and tc_playbook_db_port parameters to environment variables by default.
+ Updated ``tcprofile`` changing **logging** to **tc_log_level**.
+ Updated ``tclib`` to check for requirements.txt.

0.5.19
------
+ Updates to tcex.playbook, tcrun, and tcdata to support deleting data from Redis from previous runs.

0.5.18
------
+ Updated ``tcrun`` to handle issue where **install_json** is not defined in the **tcex.json** file and script name was improperly being set.

0.5.17
------
+ Updated create_output() method to fix issue when using output variables of the same name and different types.

0.5.16
------
+ Updated ``tcrun`` to not check for the program main file for Java Apps.

0.5.15
------
+ Initial update to ``tcrun`` to support running Java Apps.
+ Added support for **install_json** profile parameter to tcex.json. This should be included in all **tcex.json** files going forward.
+ Added support for **java_path** config parameter to tcex.json for custom java path.  Default behavior is to use the default version of **java** from user path.
+ Added support for **class_path** profile parameter to tcex.json for custom java paths.  By default ``./target/`` will be used as the class_pass value.
+ Updated ``tcpackage`` to grab minor version from programVersion in install.json.  If no programVersion found the default version of an App is 1.0.0.
+ Cleanup for PEP8 and more.

0.5.14
------
+ Updated :py:meth:`~tcex.tcex_resources.Bulk.json` method to use proper entity value.
+ Updated ``tcprofile`` to use default env values for API credentials.
+ Adding **groups** parameter to **tcex.json** so a profile can be part of multiple groups.

0.5.13
------
+ Added additional exclude values for IDE directories.
+ Added **app_name** parameter to **tcex.json** for App built on system where App directory is not the App name.
+ Updated ``tcpackage`` to use new **app_name** if exists and default back to App directory name.
+ Updated ``tcprofile`` to only output redis variable for Playbook Apps.
+ Updated ``tclib`` to have default config value for instance where there is not **tcex.json** file.

0.5.12
------
+ Update Building Apps section of the Documentation.
+ Updated required module versions (requests, python-dateutil, and redis).
+ Fixed issue with sleep parameter being ignored in ``tcrun``.
+ Updated ``tclib`` to automatically read **tcex.json**.
+ Updated ``tcpackage`` to output Apps zip files with **.tcx** extension.

0.5.11
------
+ Added support for Binary data type in ``tcdata`` for staging.

0.5.10
------
+ Added platform for docker support.

0.5.9
-----
+ Added platform check for subprocess calls.
+ Added additional error logging for ``tcrun`` command.

0.5.8
-----
+ Added better support for build / test commands on Windows platform.

0.5.7
-----
+ Removing pip as a dependency.

0.5.6
-----
+ Updated ``tcdata`` to support multiple operators for validation.
+ Added ``tcprofile`` command to automatically build testing profiles from install.json.
+ Updated ``tcrun`` to create log, out, and temp directories for testing output.
+ Updated ``tcpackage`` to exclude **.pyc** files and **__pycache__** directory.

0.5.5
-----
+ Updated ``tcpackage`` to append version number to zip_file.
+ Added a **bundle_name** parameter to tcex.json file for systems where the directory name doesn't represent the App name.

0.5.4
-----
+ Minor update on tcdata for issue with bytes string in Python 3.

0.5.3
-----
+ Added new tcdata, tclib, tcpackage, and tcrun commands for App testing and packaging (app.py will be deprecated in the future).
+ Updates to ``__main__.py`` for new lib directory structure create with pip (replaced easy_install).
+ Apps should now be built with ``requirements.txt`` instead of ``setup.py``.

0.5.2
------
+ Updated :py:meth:`~tcex.tcex_resources.Resource.association_custom` method to support DELETE/POST Methods.
+ Added :py:meth:`~tcex.tcex.TcEx._association_types` method to load Custom Association types from API.
+ Added ``indicator_types_data`` property with full Indicator Type data.
+ Added ``indicator_associations_types_data`` property with full Indicator Association Type data.

0.5.1
------
+ Update to playbookdb variable name.
+ Updated __main__.py template for proper exit code.

0.5.0
------
+ Added support for output variable of the same name, but different types.
+ Support for new TCKeyValueAPI DB types in Playbook Apps.  This is a seamless change to the Apps.
+ Updated :py:meth:`~tcex.tcex.TcEx.authorization` method to return properly formatted header when no token_expires is provided.
+ Added automatic Authorization to :py:meth:`~tcex.tcex.TcEx.request_tc` method.
+ Updated documentation for Request module.

0.4.x
=====

0.4.11
------
+ Changed proxy variable to proxies in :py:meth:`~tcex.tcex.TcEx.request_external` method.
+ Changed proxy variable to proxies in :py:meth:`~tcex.tcex.TcEx.request_tc` method.
+ Added :py:meth:`~tcex.tcex_resources.Task.assignees` method for Tasks.
+ Added :py:meth:`~tcex.tcex_resources.Task.escalatees` method for Tasks.
+ Added 201 as valid status code for Task.

0.4.10
------
+ Added :py:meth:`~tcex.tcex_resources.Resource.victims` method to :py:mod:`~tcex.tcex_resources.Resource` module.
+ Added :py:meth:`~tcex.tcex_resources.Resource.victim_assets` method to :py:mod:`~tcex.tcex_resources.Resource` module.
+ Added :py:meth:`~tcex.tcex_resources.Indicator.observations` methods to :py:mod:`~tcex.tcex_resources.Resource` module.
+ Added :py:meth:`~tcex.tcex_resources.Indicator.observation_count` methods to :py:mod:`~tcex.tcex_resources.Resource` module.
+ Added :py:meth:`~tcex.tcex_resources.Indicator.observed` methods to :py:mod:`~tcex.tcex_resources.Resource` module.
+ Changed private ``_copy()`` method to public :py:meth:`~tcex.tcex_resources.Resource.copy` in the :py:mod:`~tcex.tcex_resources.Resource` module.
+ Updated :py:meth:`~tcex.tcex_resources.File.occurrence` method indicator parameter to be optional.
+ Added :py:meth:`~tcex.tcex_resources.Host.resolution` methods to :py:mod:`~tcex.tcex_resources.Resource` module to retrieve DNS resolutions on Host Indicators.

0.4.9
-----
+ Added :py:meth:`~tcex.tcex_resources.Signature.download` method to download signature data.
+ Added urlencoding to proxy user and password.

0.4.7
-----
+ Added :py:meth:`~tcex.tcex.TcEx.job` method to allow multiple jobs to run in an App.
+ Update :py:meth:`~tcex.tcex.TcEx.s` method to fix issues in Python 3.

0.4.6
-----
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.create_binary_array` method to properly handle binary array data.
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_binary_array` method to properly handle binary array data.

0.4.5
-----
+ Updated :py:meth:`~tcex.tcex_resources.Indicator.indicator_body` to support missing hashes.
+ Added :py:meth:`~tcex.tcex_resources.Indicator.false_positive` endpoint for indicators.
+ Merged pull requests for better native Python3 support.
+ Added Campaign to group types.
+ Increased request timeout to 300 seconds.

0.4.4
-----
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method logic for null values and better support of mixed values.

0.4.3
-----
+ Update to TcExJob module for file hashes updates using v2/indicators/files.

0.4.2
-----
+ Update to :py:mod:`~tcex.tcex_job.TcExJob` module for file hashes updates using ``v2/indicators/files``.

0.4.2
-----
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to support different formatting dependent on the parent variable type.
+ Updated :py:mod:`~tcex.tcex_resources.Resource` module for an issue where copying the instance causing errors with request instance in Python3.
+ Updated TcExLocal :py:meth:`~tcex.tcex_local.TcExLocal.run` method to better format error output.

0.4.1
-----
+ Adding :py:meth:`~tcex.tcex_resources.DataStore.add_payload` method to :py:mod:`~tcex.tcex_resources.DataStore` class.
+ Fixed issue with :py:mod:`~tcex.tcex_job.TcExJob` module where batch indicator POST with chunking would fail after first chunk.
+ Added :py:meth:`~tcex.tcex.TcEx.safe_indicator` method to urlencode and cleanup indicator before associations, etc.
+ Updated :py:meth:`~tcex.tcex.TcEx.expand_indicators` method to use a regex instead of split for better support of custom indicators.
+ Updated :py:mod:`~tcex.tcex_job.TcExJob._process_indicators_v2` to better handle custom indicator types.
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to strip off double quote from JSON string on mixed types and to decode escaped strings.
+ Updated :py:mod:`~tcex.tcex_resources.Resource` module so that all indicator are URL encoded before adding to the URI.
+ Updated :py:meth:`~tcex.tcex_resources.Indicator.indicator_body` method to only include items in the JSON body if not None.
+ Updated :py:meth:`~tcex.tcex_resources.Indicator.indicators` method to handle extra white spaces on the boundary.
+ Added additional standard args of ``api_default_org`` and ``tc_in_path``.

0.4.0
-----
+ Breaking change to :py:mod:`~tcex.tcex_resources.Resource` module. All ``_pivot()`` and ``associations()`` methods now take a instance of Resource and return a copy of the current Resource instance. Other methods such as ``security_label()`` and ``tags()`` now return a copy of the current Resource instance.
+ Added :py:mod:`~tcex.tcex_resources.Tag` Resource class.
+ Added :py:meth:`~tcex.tcex.TcEx.resource` method to get instance of Resource instance.
+ Added :py:mod:`~tcex.tcex_resources.DataStore` Resource class to the :py:mod:`~tcex.tcex_resources.Resource` module.
+ Updated :py:mod:`~tcex.tcex_job.TcExJob` module for changes in the :py:mod:`~tcex.tcex_resources.Resource` module.

0.3.x
=====

0.3.7
-----
+ Added logic around retrieving Batch Errors to handle 404.
+ Added new :py:meth:`~tcex.tcex_playbook.TcExPlaybook.exit` method for playbook apps (exit code of 3 to 1 for partial success).

0.3.6
-----
+ Added :py:mod:`~tcex.tcex_job.TcExJob.group_results` and :py:mod:`~tcex.tcex_job.TcExJob.indicator_results` properties to :py:mod:`~tcex.tcex_job.TcExJob` module.
+ Added :py:meth:`~tcex.tcex.TcEx.request_external` and :py:meth:`~tcex.tcex.TcEx.request_tc` methods.
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method with a better regex for matching variables.
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook` module with better error handling with JSON loads.
+ Updated TcExLocal :py:meth:`~tcex.tcex_local.TcExLocal.run` method to sleep after subprocess executes the first time.

0.3.5
-----
+ Updated :py:mod:`~tcex.tcex_job.TcExJob` module to allow indicators to be added via ``/v2/indicators/<type>``.
+ Updated structure for attributes/tags adds on groups to use singular version (attribute/tag) in Jobs modules to match format used for Indicators.
+ Added custom, case_preference and parsable properties to :py:mod:`~tcex.tcex_resources.Resource` module.
+ Added logic to cleanup temporary JSON bulk file. When logging is "debug" a compressed copy of the file will remain.

0.3.4
-----
+ Fixed issue in :py:mod:`~tcex.tcex_resources` module with pagination stopping before all results are retrieved.

0.3.3
-----
+ Added :py:meth:`~tcex.tcex.TcEx.s` method to replace the :py:meth:`~tcex.tcex.TcEx.to_string` method (handle bad unicode in Python2 and still support Python3).
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to better handle embedded Vars.

0.3.2
-----
+ Added :py:meth:`~tcex.tcex_resources.Resource.indicators` method to allow iteration over indicator values in Indicator response JSON.

0.3.1
-----
+ Updated :py:meth:`~tcex.tcex_request.TcExRequest.set_basic_auth` method to use proper unicode method.
+ Updated :py:mod:`~tcex.tcex_playbook` create and read methods to warn when None value is passed.

0.3.0
-----
+ Added :py:meth:`~tcex.tcex_request.TcExRequest.json` method that accepts a dictionary and automatically sets content-type and body.
+ Updated :py:meth:`~tcex.tcex.TcEx.safeurl` and :py:meth:`~tcex.tcex.TcEx.safetag` to use :py:meth:`~tcex.tcex.TcEx.to_string`.
+ Update :py:meth:`~tcex.tcex_request.TcExRequest.set_basic_auth` for 2/3 compatibility.

0.2.x
=====

0.2.11
------
+ Updated :py:meth:`~tcex.tcex_request.TcExRequest.add_payload` method to not force the value to string.
+ Updated :py:meth:`~tcex.tcex_request.TcExRequest.files` method.
+ Added :py:meth:`~tcex.tcex_request.TcExRequest.set_basic_auth` method for instance where normal method does not work.

0.2.10
------
+ Added :py:meth:`~tcex.tcex_request.TcExRequest.files` property to :py:mod:`~tcex.tcex_request` module.

0.2.9
-----
+ Fixed issue with boolean parameters having an extra space at the end.

0.2.8
-----
+ Updated :py:meth:`~tcex.tcex_local.TcExLocal._parameters` method to build a list for subprocess.popen instead of a string.
+ Updated install.json schema to support **note** field.

0.2.7
-----
+ Remove hiredis as a dependency.
+ Added hvac as a dependency for vault credential storage.
+ Added ability to use Vault as a credential store for local testing.
+ Fix to Args wrapper for Windows (' to ").

0.2.6
-----
+ Added sleep option for test profiles that take time to complete.

0.2.5
-----
+ Update to :py:mod:`~tcex.tcex_local` module to change tc.json profiles to list instead of dictionary to maintain order of profiles.
+ Added feature to :py:mod:`~tcex.tcex_local` to read environment variables for value in tc.json (e.g. $evn.my_api_key).

0.2.4
-----
+ Handle None type returned by Redis module.

0.2.3
-----
+ Added :py:meth:`~tcex.tcex.TcEx.to_string` method to replace old ``uni()`` method (handle Python 2/3 encoding for apps).

0.2.2
-----
+ Update for string, unicode, bytes issue between Python 2/3

0.2.1
-----
+ Update of :py:mod:`~tcex.tcex_local` module for Python 2/3 support.
+ Update binary methods in :py:mod:`~tcex.tcex_playbook` module for Python 2/3 support.

0.2.0
-----
+ Rework of :py:mod:`~tcex.tcex_local` :py:meth:`~tcex.tcex_local.TcExLocal.run` logic to support updated tc.json schema.
+ Changed **--test** arg to **--profile** in :py:meth:`~tcex.tcex_local.TcExLocal._required_arguments`.
+ Added **script** field to tc.json that matches **--script** arg to support predefined script names.
+ Added **group** field to tc.json that matches **--group** arg in :py:meth:`~tcex.tcex_local.TcExLocal._required_arguments` to support running multiple profiles.
+ Added `inflect <https://pypi.python.org/pypi/inflect>`_ requirement version 0.2.5.
+ Changed python-dateutil requirement to version 2.6.10.
+ Changed requests requirement to version 2.13.0.

0.1.x
=====

0.1.6
-----
+ Added accepted status code of 201 for Custom Indicator POST on dynamic class creation.

0.1.5
-----
+ Added :py:meth:`~tcex.tcex_resources.Indicator.entity_body` method to :py:mod:`~tcex.tcex_resources` for generating indicator body.
+ Added :py:meth:`~tcex.tcex_resources.Indicator.indicator_body` method to :py:mod:`~tcex.tcex_resources` for generating indicator body.

0.1.4
-----
+ Fixed issue with Job :py:meth:`~tcex.tcex_job.TcExJob.group_cache` method.

0.1.3
-----
+ Updated :py:mod:`~tcex.tcex_job.TcExJob` module to use new pagination functionality in :py:mod:`~tcex.tcex_resources` module.
+ Updated and labeled :py:meth:`~tcex.tcex_resources.Resource.paginate` method as deprecated.

0.1.2
-----
+ Updated tcex_local for additional parameter support during build process.

0.1.1
-----
+ Update tcex_local for exit code when app.py is called (maven build issue).
+ Added new log event for proxy settings.

0.1.0
-----
+ Reworked iterator logic in :py:mod:`~tcex.tcex_resources` module.

0.0.x
=====

0.0.12
------
+ Documentation updates.
+ Changes to :py:mod:`~tcex.tcex_resources` to allow iteration over the instance to retrieve paginated results.
+ Updates to support persistent args when running app locally.
+ Updated playbook module for Python 3.
+ Added logging of platform for debugging purposes.
+ Cleanup and Pep 8 changes.

0.0.11
------
+ Updated :py:meth:`~tcex.tcex_job.TcExJob.file_occurrence` in the :py:mod:`~tcex.tcex_job.TcExJob` module.
+ Added :py:mod:`~tcex.tcex_data_filter` module accessed via ``tcex.data_filter(data)``.
+ Added :py:meth:`~tcex.tcex.TcEx.epoch_seconds` method to return epoch seconds with optional delta period.
+ Added ``python-dateutil==2.4.2`` as a Python dependency.

0.0.10
------
+ Added :py:meth:`~tcex.tcex_resources.Resource.paginate` method to :py:mod:`~tcex.tcex_resources` module.
+ Updated :py:meth:`~tcex.tcex_job.TcExJob.group_cache` module to use :py:meth:`~tcex.tcex_resources.Resource.paginate` method.

0.0.9
-----
+ Updated :py:mod:`~tcex.tcex_job.TcExJob` module for :py:mod:`~tcex.tcex_resources` modules renamed methods and changes.

0.0.8
-----
+ Change logging level logic to use ``logging`` over ``tc_logging_level`` if it exist.
+ Added App version logging attempt.


0.0.7
-----
+ Updated :py:meth:`~tcex.tcex.TcEx._resources` method to handle TC version without custom indicators.
+ Updated logging to better debug API request failures.
+ Updated package command to create lib directory with python version (e.g. lib_3.6.0)
+ Logging the Logging Level, Python and TcEx version for additional debugging.

0.0.6
-----
+ Updated open call for bytes issue on Python 3

0.0.5
-----
+ Updated to setup.py for Python 3 support

0.0.4
-----
+ Update for Campaign resource type Class.
+ Added :ref:`building_apps` and :ref:`development_tools` section to documentation.

0.0.3
-----
+ Added :py:meth:`~tcex.tcex_resources.Campaign` Class.
+ Multiple updates to documentation

0.0.2
-----
+ Updates to ``setup.py`` for build

0.0.1
-----
+ Initial Public Release

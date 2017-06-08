.. _release_notes:

Release Notes
#############

0.4.x
=====

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
+ Updated :py:meth:`~tcex.tcex_playbook.TcExPlaybook.read_embedded` method to support different formatting dependent on the parent varibable type.
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
+ Updated :py:mod:`~tcex.tcex_playbook` create and read methods to warn when None vaule is passed.

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
+ Logging the Logging Level, Python and TcEx verison for additional debugging.

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

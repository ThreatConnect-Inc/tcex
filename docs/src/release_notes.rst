.. _release_notes:

Release Notes
#############

0.3.x
=====

0.3.2
------
+ Added :py:meth:`~tcex.tcex_resources.Resource.indicators` method to allow iteration over indicator values in Indicator response JSON.

0.3.1
------
+ Updated :py:meth:`~tcex.tcex_request.TcExRequest.set_basic_auth` method to use proper unicode method.
+ Updated :py:mod:`~tcex.tcex_playbook` create and read methods to warn when None vaule is passed.

0.3.0
------
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

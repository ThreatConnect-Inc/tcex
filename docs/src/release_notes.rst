.. _release_notes:

==============
Release Notes
==============

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
------
+ Updated :py:mod:`~tcex.tcex_job.TcExJob` module for :py:mod:`~tcex.tcex_resources` modules renamed methods and changes.

0.0.8
------
+ Change logging level logic to use ``logging`` over ``tc_logging_level`` if it exist.
+ Added App version logging attempt.


0.0.7
------
+ Updated :py:meth:`~tcex.tcex.TcEx._resources` method to handle TC version without custom indicators.
+ Updated logging to better debug API request failures.
+ Updated package command to create lib directory with python version (e.g. lib_3.6.0)
+ Logging the Logging Level, Python and TcEx verison for additional debugging.

0.0.6
------
+ Updated open call for bytes issue on Python 3

0.0.5
------
+ Updated to setup.py for Python 3 support

0.0.4
------
+ Update for Campaign resource type Class.
+ Added :ref:`building_apps` and :ref:`development_tools` section to documenation.

0.0.3
------
+ Added :py:meth:`~tcex.tcex_resources.Campaign` Class.
+ Multiple updates to documenation

0.0.2
------
+ Updates to ``setup.py`` for build

0.0.1
------
+ Initial Public Release

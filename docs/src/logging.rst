.. _logging:

========
Logging
========
The TcEx module has a built-in :py:meth:`~tcex.tcex.TcEx._logger` method that will log to the ``args.tc_log_path`` directory. If the job is running with a **API Token** and ``args.tc_log_to_api`` is enabled the logger will automatically log to the API.  This logger is a instance of the standard Python logger with modification for API logging.

.. Note:: The ``args.tc_log_to_api`` variable is passed only if API Logging in turned on in System Settings.

Example Logging::

    # logging examples
    tcex.log.debug('logging debug')
    tcex.log.info('logging info')
    tcex.log.error('logging error')
    tcex.log.critical('logging critical')

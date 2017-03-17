.. include:: <isonum.txt>
.. _logging:

=======
Logging
=======
The ThreatConnect |trade| TcEx App Framework has a built-in logger that will log to the ``args.tc_log_path`` directory. If the App is passed ``args.tc_token`` and ``args.tc_log_to_api`` the logger will automatically log to the ThreatConnect API.  This built-in logger is a instance of the standard `Python Logger <https://docs.python.org/2/library/logging.html>`_ with modification for API logging.

.. Note:: The ``args.tc_log_to_api`` variable is passed only if API Logging in turned on in the System Settings in the ThreatConnect Platform UI.

**Example Logging**

.. code-block:: python
    :linenos:
    :lineno-start: 1

    tcex.log.debug('logging debug')
    tcex.log.info('logging info')
    tcex.log.warning('logging warning')
    tcex.log.error('logging error')
    tcex.log.critical('logging critical')
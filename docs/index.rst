======
 TcEx
======

------------------------------------------------------------------
Python helper module for ThreatConnect Exchange and Playbook Apps
------------------------------------------------------------------

Release v\ |version|. (:ref:`Installation <install>`)

Base Class
------------------
The base TcEx Class provides common method used in ThreatConnect Exchange apps as well as an
app logger that supports automatic logging to the ThreatConnect API logging endpoint.


Logging
------------------
The TcEx module has a built-in logger method (:py:meth:`tcex.TcEx._logger`) that will log to the ``args.tc_log_path`` directory. If the job is running with a **API Token** and ``args.tc_log_to_api`` is enabled (configure via the UI in System Settings) the logger will automatically log to the API.  This logger is a instance of the standard Python logger with modification for API logging.

Example Logging::

    # logging examples
    tcex.log.debug('logging debug')
    tcex.log.info('logging info')
    tcex.log.error('logging error')
    tcex.log.critical('logging critical')

Parser / Args
------------------
The :py:meth:`tcex.TcEx` Class provides the :py:meth:`tcex.TcEx.parser` method which returns and instance of :py:meth:`argparser`.

Example::

    from tcex import TcEx
    parser = tcex.parser
    parser.add_argument('--owner', help='Destination Owner', required=True)
    args = tcex.args

Authorization (Token/HMAC)
---------------------------

Message TC
------------------

Results TC
------------------

Requests
------------------

Proxies
------------------

Exit
------------------

Resources
------------------

Jobs
------------------

Playbooks
------------------


Commonly used features

- International Domains and URLs
- Keep-Alive & Connection Pooling
- Sessions with Cookie Persistence

The User Guide
--------------

This part of the documentation, which is mostly prose, begins with some
background information about Requests, then focuses on step-by-step
instructions for getting the most out of Requests.

.. toctree::
   :caption:  Table of Contents
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
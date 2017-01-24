.. include:: <isonum.txt>
.. _parser:

=============
Parser / Args
=============
The ThreatConnect |trade| TcEx App Framework provides the :py:mod:`~tcex.tcex.TcEx.parser` property which returns and instance of ``argparser.ArgParser``. This argparser instance is an extension of the Python argparser method with predefined arguments specifically for ThreatConnect Exchange Apps. Once all custom arguments are added ``args`` can be access with the :py:mod:`~tcex.tcex.TcEx.args` property.

API Arguments
-------------
Argument in the API argument section are provided for authorization to the ThreatConnect API.  If the ``tc_token`` argument is passed it has priority over the HMAC arguments. The TcEx Framework automatically handles all these arguments and makes them available via the :py:mod:`~tcex.tcex.TcEx.args` property.

.. Note:: The ``api_access_id`` and ``api_secret_key`` arguments have to be configured in the :ref:`install_json` configuration file and configured in each job to be passed to the app.  The ``tc_token`` will automatically be passed for Apps running in the ThreatConnect Exchange Platform.

The list of API args can be found in the :py:meth:`~tcex.argparser.ArgParser._api_arguments` method.

Batch Arguments
---------------
The ThreatConnect batch API endpoint requires a few arguments for setting the batch job.  These arguments have sane default values and are not often required to be added to the ``install.json`` configuration file.  These default values can also be overridden with methods provided in the :py:mod:`~tcex.tcex_job.TcExJob` module.

The list of Batch args can be found in the :py:meth:`~tcex.argparser.ArgParser._batch_arguments` method.

Playbook Arguments
------------------
Playbook Apps have a standard set of arguments. All of these argument will be passed by the ThreatConnect Exchange Platform for all Playbook apps.

The list of Playbook args can be found in the :py:meth:`~tcex.argparser.ArgParser._playbook_arguments` method.

Standard Arguments
------------------
The ThreatConnect Platform passes all apps a set of standard arguments.  Some of these arguments are depended on App settings and others on System settings.  The TcEx Framework automatically handles all these arguments and makes them available via the :py:mod:`~tcex.tcex.TcEx.args` property.

The list of standard args can be found in the :py:meth:`~tcex.argparser.ArgParser._standard_arguments` method.

Custom Argument
---------------
Custom arguments can be added to the ``argparser.ArgParser`` instance of :py:mod:`~tcex.tcex.TcEx.parser`

**Example**

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 4-6

    from tcex import TcEx

    tcex = TcEx()
    parser = tcex.parser
    parser.add_argument('--myarg', help='My Custom Argument', required=True)
    args = tcex.args

    <snipped...>
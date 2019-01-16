.. include:: <isonum.txt>
.. _exit:

====
Exit
====
All ThreatConnect |copy| Exchange Apps should deliberately exit with the appropriate exit code on successful or failed execution. The :py:mod:`~tcex.tcex.TcEx` Framework provides the :py:meth:`~tcex.tcex.TcEx.exit` method and :py:mod:`~tcex.tcex.TcEx.exit_code` property to handle exit codes.  All Apps should end with the :py:meth:`~tcex.tcex.TcEx.exit` method.

The :py:meth:`~tcex.tcex.TcEx.exit` method supports and optional ``msg`` parameter.  If provided the ``msg`` value will be logged and written to the ``message_tc`` file as the App exit message.

.. Important:: Providing a proper exit code for Playbook Apps is important for execution of downstream Apps. Supported exit codes for Playbook Apps are 0 (success) and 1 (failure).

.. Note:: The exit methods automatically logs the exit code using the :ref:`logging` functionality of the TcEx Framework.

Setting Exit Code
=================
Some failures do not warrant an immediate exit.  In such case the :py:mod:`~tcex.tcex.TcEx.exit_code` property allows an exit code to be set for when the :py:meth:`~tcex.tcex.TcEx.exit` method is called.  This allows the app to continue execution and still notify the ThreatConnect Platform that a failure occurred.

Job App Example
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 8,12

    tcex = TcEx()

    <...snipped>
    try:
        with open(datafile, 'r') as fh:
            data = fh.read()
    except:
        tcex.exit_code = 3

    <snipped...>

    tcex.exit(msg='My App message')

Playbook App Example
--------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 8,12

    tcex = TcEx()

    <...snipped>
    try:
        with open(datafile, 'r') as fh:
            data = fh.read()
    except:
        tcex.exit_code = 3

    <snipped...>

    tcex.playbook.exit(msg='My App message')

Immediate Exit on Failure
=========================
Certain failures require that the App exit immediately.  In these cases calling the :py:meth:`~tcex.tcex.TcEx.exit` method while passing the exit code will immediately halt execution of the App and notify the ThreatConnect Platform of a failure.

Job App Example
---------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 8

    tcex = TcEx()

    <...snipped>
    try:
        with open(datafile, 'r') as fh:
            data = fh.read()
    except:
        tcex.exit(1, 'App failed')

    <snipped...>

Playbook App Example
--------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 8

    tcex = TcEx()

    <...snipped>
    try:
        with open(datafile, 'r') as fh:
            data = fh.read()
    except:
        tcex.playbook.exit(1, 'App failed')

    <snipped...>

Job App Exit Codes
==================

+ 0 - Successful execution of App
+ 1 - Failed execution of App
+ 3 - Partial failure of App

Playbook App Exit Codes
=======================

+ 0 - Successful execution of App
+ 1 - Failed execution of App

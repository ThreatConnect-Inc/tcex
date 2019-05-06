.. include:: <isonum.txt>
.. _module_utils:

==============
Module: Utils
==============
The ThreatConnect TcEx App Framework provides common **utils** methods to assist in writing Apps.

Format DateTime
================
The :py:mod:`~tcex.tcex_utils.TcExUtils.format_datetime` method accepts multiple input types and returns an ISO-formatted datetime string by default.  Optionally, the timezone of the timestamp can be provided as well as the **strftime** format.

Accepted Formats:

#. Human Input (e.g., 30 days ago, last Friday)
#. ISO 8601 (e.g., 2017-11-08T16:52:42Z)
#. "Loose" Date format (e.g., 2017 12 25)
#. UNIX® Time/POSIX Time/Epoch Time (e.g., 1510686617 or 1510686617.298753)

.. note:: This module supports the use of ``%s`` to retrieve the datetime in UNIX format.

UNIX Timestamp Integer
----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime(1510052400)
    <snipped...>

UNIX Timestamp String
---------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('1510686617.298753')
    <snipped...>

ISO 8601 Date (Zulu)
--------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('2017-11-08T16:52:42Z')
    <snipped...>

ISO 8601 Date (Zulu) in U.S. Eastern Time
-----------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('2017-11-08T16:52:42Z', 'US/Eastern')
    <snipped...>

ISO 8601 Date with Timezone Offset
----------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('2017-11-08T16:52:42-05:00')
    <snipped...>

ISO 8601 Date with Timezone Offset in U.S. Eastern Time
-------------------------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('2017-11-08T16:52:42-00:00', 'US/Eastern')
    <snipped...>

Now UTC UNIX timestamp
----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('now', date_format='%s')
    <snipped...>

Now in U.S. Central Time
------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('now', 'US/Central')
    <snipped...>

Tomorrow at 6 A.M.
------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('tomorrow at 6 am')
    <snipped...>

Next Monday at Noon
-------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('next monday at noon')
    <snipped...>

3 Weeks Ago U.S. Eastern Time Formatted for ThreatConnect
---------------------------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('3 weeks ago', 'US/Eastern', '%Y-%m-%dT%H:%M:%SZ')
    <snipped...>

Date to Datetime
================
The :py:mod:`~tcex.tcex_utils.TcExUtils.date_to_datetime` method uses the **dateutil** module to parse the provided data and return a **datetime.datetime** object.

Human Time to Datetime
======================
The :py:mod:`~tcex.tcex_utils.TcExUtils.human_date_to_datetime` method uses the **parsedatetime** module to parse the provided data and return a **datetime.datetime** object.

Examples:

* August 25, 2008
* 25 Aug 2008
* Aug 25, 5 p.m.
* 5 p.m., August 25
* next Saturday
* tomorrow
* next Thursday at 4 p.m.
* at 4 p.m,
* eod
* tomorrow eod
* eod Tuesday
* eoy
* eom
* in 5 minutes
* 5 minutes from now
* 5 hours before now
* 2 hours before noon
* 2 days from tomorrow

UNIX Time to Datetime
=====================
The :py:mod:`~tcex.tcex_utils.TcExUtils.unix_time_to_datetime` method converts a UNIX timestamp to a **datetime.datetime** object.

Examples:

* 1510686617
* 1510686617.298753

UNIX® is a registered trademark of The Open Group.

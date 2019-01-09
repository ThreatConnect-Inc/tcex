.. include:: <isonum.txt>
.. _module_utils:

==============
Module - Utils
==============
The ThreatConnect |copy| TcEx App Framework provides common *utils* methods to assist in writing Apps.

Format Date Time
================
The :py:mod:`~tcex.tcex_utils.TcExUtils.format_datetime` method accepts multiple input types and returns an ISO formated datetime string by default.  Optionally the timezone of the timestamp can be provided as well as the **strftime** format.

Accepted Formats:

#. Human Input (e.g 30 days ago, last friday)
#. ISO 8601 (e.g. 2017-11-08T16:52:42Z)
#. "Loose" Date format (e.g. 2017 12 25)
#. Unix Time/Posix Time/Epoch Time (e.g. 1510686617 or 1510686617.298753)

.. note:: This module supports using ``%s`` to retrieve the datetime in Unix format.

Unix Timestamp Integer
----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime(1510052400)
    <snipped...>

Unix Timestamp String
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

ISO 8601 Date (Zulu) in US/Eastern Time
---------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('2017-11-08T16:52:42Z', 'US/Eastern')
    <snipped...>

ISO 8601 Date w/ TZ Offset
--------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('2017-11-08T16:52:42-05:00')
    <snipped...>

ISO 8601 Date w/ TZ Offset in US/Eastern Time
---------------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('2017-11-08T16:52:42-00:00', 'US/Eastern')
    <snipped...>

Now UTC Unix timestamp
----------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('now', date_format='%s')
    <snipped...>

Now Central
-----------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('now', 'US/Central')
    <snipped...>

Tomorrow at 6 AM
----------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('tomorrow at 6 am')
    <snipped...>

Next Monday at noon
-------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('next monday at noon')
    <snipped...>

3 Weeks Ago US/Eastern Formatted for ThreatConnect
--------------------------------------------------

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 2

    <...snipped>
    tcex.utils.format_datetime('3 weeks ago', 'US/Eastern', '%Y-%m-%dT%H:%M:%SZ')
    <snipped...>

Date to Datetime
================
The :py:mod:`~tcex.tcex_utils.TcExUtils.date_to_datetime` method uses the dateutil module to parse the provided data and return a datetime.datetime object.

Human Time to Datetime
======================
The :py:mod:`~tcex.tcex_utils.TcExUtils.human_date_to_datetime` method uses the parsedatetime module to parse the provided data and return a datetime.datetime object.

Examples:

* August 25th, 2008
* 25 Aug 2008
* Aug 25 5pm
* 5pm August 25
* next saturday
* tomorrow
* next thursday at 4pm
* at 4pm
* eod
* tomorrow eod
* eod tuesday
* eoy
* eom
* in 5 minutes
* 5 minutes from now
* 5 hours before now
* 2 hours before noon
* 2 days from tomorrow

Unix Time to Datetime
=====================
The :py:mod:`~tcex.tcex_utils.TcExUtils.unix_time_to_datetime` method converts a unix timestamp to a datetime.datetime object.

Examples:

* 1510686617
* 1510686617.298753

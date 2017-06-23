.. include:: <isonum.txt>
.. _resources:

=========
Resources
=========

The ThreatConnect |trade| TcEx Framework provides access to the ThreatConnect API using the :py:mod:`~tcex.tcex_resources` module.  The Resource Classes can be accessed via the ``tcex.resources`` property of the TcEx Framework.

**Direct Access**

.. code-block:: python
    :emphasize-lines: 3-5

    tcex = TcEx()

    resource = tcex.resources.Adversary(tcex)
    # paginate over results
    for result in resource:
        print(result['status'])
        print(result['data'])

    tcex.exit()

**Dynamic Access**

.. code-block:: python
    :emphasize-lines: 3-5

    tcex = TcEx()

    resource = tcex.resource('User Agent')
    # paginate over results
    for result in resource:
        print(result['status'])
        print(result['data'])

    tcex.exit()

.. Note:: For result sets that do not support pagination the ``resource.request()`` method can be called directly.

Data Store Resource
--------------------
The TcEx Module provide CRUD (Create, Read, Update, and Delete) operations to the ThreatConnect DataStore. The DataStore provides access to three domains: Local; Organization; and System.

+------------------------+----------------------------------------------------------+
| Db Method              | Method                                                   |
+========================+==========================================================+
| Create                 | :py:meth:`~tcex.tcex_resources.DataStore.create`         |
+------------------------+----------------------------------------------------------+
| Read                   | :py:meth:`~tcex.tcex_resources.DataStore.read`           |
+------------------------+----------------------------------------------------------+
| Update                 | :py:meth:`~tcex.tcex_resources.DataStore.update`         |
+------------------------+----------------------------------------------------------+
| Delete                 | :py:meth:`~tcex.tcex_resources.DataStore.delete`         |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`examples`

Group Resources
---------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Group (Base)           | :py:class:`~tcex.tcex_resources.Group`                   |
+------------------------+----------------------------------------------------------+
| Adversary              | :py:class:`~tcex.tcex_resources.Adversary`               |
+------------------------+----------------------------------------------------------+
| Campaign               | :py:class:`~tcex.tcex_resources.Campaign`                |
+------------------------+----------------------------------------------------------+
| Document               | :py:class:`~tcex.tcex_resources.Document`                |
+------------------------+----------------------------------------------------------+
| Email                  | :py:class:`~tcex.tcex_resources.Email`                   |
+------------------------+----------------------------------------------------------+
| Incident               | :py:class:`~tcex.tcex_resources.Incident`                |
+------------------------+----------------------------------------------------------+
| Signature              | :py:class:`~tcex.tcex_resources.Signature`               |
+------------------------+----------------------------------------------------------+
| Threat                 | :py:class:`~tcex.tcex_resources.Threat`                  |
+------------------------+----------------------------------------------------------+

Indicator Resources
-------------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Indicator (Base)       | :py:class:`~tcex.tcex_resources.Indicator`               |
+------------------------+----------------------------------------------------------+
| Address                | :py:class:`~tcex.tcex_resources.Address`                 |
+------------------------+----------------------------------------------------------+
| EmailAddress           | :py:class:`~tcex.tcex_resources.EmailAddress`            |
+------------------------+----------------------------------------------------------+
| File                   | :py:class:`~tcex.tcex_resources.File`                    |
+------------------------+----------------------------------------------------------+
| Host                   | :py:class:`~tcex.tcex_resources.Host`                    |
+------------------------+----------------------------------------------------------+
| URL                    | :py:class:`~tcex.tcex_resources.URL`                     |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`examples`

.. Note:: Custom Indicators can be accessed by the **Type**. The ThreatConnect platform supports Custom indicator types with a space in the name. To prevent issues with the space all Custom Resource (Indicator) types should be made **safe** by using the :py:meth:`~tcex.tcex.TcEx.safe_rt` method.

Owner Resources
---------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Owner                  | :py:class:`~tcex.tcex_resources.Owner`                   |
+------------------------+----------------------------------------------------------+

Security Label Resources
------------------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| SecurityLabel          | :py:class:`~tcex.tcex_resources.SecurityLabel`           |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`examples`

Tag Resources
---------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Tag                    | :py:class:`~tcex.tcex_resources.Tag`                     |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`examples`

Task Resources
--------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Task                   | :py:class:`~tcex.tcex_resources.Task`                    |
+------------------------+----------------------------------------------------------+

Victim Resources
----------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Victim                 | :py:class:`~tcex.tcex_resources.Victim`                  |
+------------------------+----------------------------------------------------------+
.. include:: <isonum.txt>
.. _module_resources:

==================
Module - Resources
==================

The ThreatConnect |copy| TcEx Framework provides access to the ThreatConnect API using the :py:mod:`~tcex.tcex_resources` module.  The Resource Classes can be accessed directly via the ``tcex.resources`` property of the TcEx Framework or indirectly vi the ``tcex.resource()`` method.

**Direct Access**

.. Important:: The Direct Access method is not supported on Custom Indicator Types.

.. code-block:: python
    :linenos:
    :lineno-start: 1
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
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 3-5

    tcex = TcEx()

    resource = tcex.resource('User Agent')
    # paginate over results
    for result in resource:
        print(result['status'])
        print(result['data'])

    tcex.exit()

.. Note:: For result sets that do not support pagination the ``resource.request()`` method can be called directly.

Custom Metrics Resource
-----------------------
The TcEx Resource Module provides Access to the ``customMetric`` API endpoint to create configurations and add data.

.. Important:: Available in 5.4+ version of the ThreatConnect API.

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Custom Metrics         | :py:class:`~tcex.tcex_resources.CustomMetric`            |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`custom_metric_examples`


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
:ref:`datastore_examples`

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
:ref:`indicator_examples`

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
:ref:`security_label_examples`

Tag Resources
---------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Tag                    | :py:class:`~tcex.tcex_resources.Tag`                     |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`tag_examples`

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

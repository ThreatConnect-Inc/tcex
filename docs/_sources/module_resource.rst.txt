.. include:: <isonum.txt>
.. _module_resources:

.. danger:: The resource module is deprecated.  The framework now has a new TI (Threat Intel) module that provides the same functionality.

==================
Module: Resources
==================

The ThreatConnect TcEx Framework provides access to the ThreatConnect API using the :py:mod:`~tcex.resources` module.  The Resource Classes can be accessed directly via the ``tcex.resources`` property of the TcEx Framework or indirectly via the ``tcex.resource()`` method.

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

.. Note:: For result sets that do not support pagination, the ``resource.request()`` method can be called directly.

Custom Metric Resources
-----------------------
The TcEx Resource Module provides Access to the ``customMetric`` API endpoint to create configurations and add data.

.. Important:: Custom Metrics are available in 5.4+ versions of the ThreatConnect API.

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Custom Metric          | :py:class:`~tcex.resources.CustomMetric`                 |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`custom_metric_examples`


Data Store Resources
--------------------
The TcEx Module provide CRUD (Create, Read, Update, and Delete) operations to the ThreatConnect DataStore. The DataStore provides access to three domains: Local, Organization, and System.

+------------------------+----------------------------------------------------------+
| Db Method              | Method                                                   |
+========================+==========================================================+
| Create                 | :py:meth:`~tcex.resources.DataStore.create`              |
+------------------------+----------------------------------------------------------+
| Read                   | :py:meth:`~tcex.resources.DataStore.read`                |
+------------------------+----------------------------------------------------------+
| Update                 | :py:meth:`~tcex.resources.DataStore.update`              |
+------------------------+----------------------------------------------------------+
| Delete                 | :py:meth:`~tcex.resources.DataStore.delete`              |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`datastore_examples`

Group Resources
---------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Group (Base)           | :py:class:`~tcex.resources.Group`                        |
+------------------------+----------------------------------------------------------+
| Adversary              | :py:class:`~tcex.resources.Adversary`                    |
+------------------------+----------------------------------------------------------+
| Campaign               | :py:class:`~tcex.resources.Campaign`                     |
+------------------------+----------------------------------------------------------+
| Document               | :py:class:`~tcex.resources.Document`                     |
+------------------------+----------------------------------------------------------+
| Email                  | :py:class:`~tcex.resources.Email`                        |
+------------------------+----------------------------------------------------------+
| Incident               | :py:class:`~tcex.resources.Incident`                     |
+------------------------+----------------------------------------------------------+
| Signature              | :py:class:`~tcex.resources.Signature`                    |
+------------------------+----------------------------------------------------------+
| Threat                 | :py:class:`~tcex.resources.Threat`                       |
+------------------------+----------------------------------------------------------+

Indicator Resources
-------------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Indicator (Base)       | :py:class:`~tcex.resources.Indicator`                    |
+------------------------+----------------------------------------------------------+
| Address                | :py:class:`~tcex.resources.Address`                      |
+------------------------+----------------------------------------------------------+
| EmailAddress           | :py:class:`~tcex.resources.EmailAddress`                 |
+------------------------+----------------------------------------------------------+
| File                   | :py:class:`~tcex.resources.File`                         |
+------------------------+----------------------------------------------------------+
| Host                   | :py:class:`~tcex.resources.Host`                         |
+------------------------+----------------------------------------------------------+
| URL                    | :py:class:`~tcex.resources.URL`                          |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`indicator_examples`

.. Note:: Custom Indicators can be accessed by **type**. The ThreatConnect platform supports Custom Indicator types with a space in the name. To prevent issues with the space all Custom Resource (Indicator) types should be made **safe** by using the :py:meth:`~tcex.tcex.TcEx.safe_rt` method.

Owner Resources
---------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Owner                  | :py:class:`~tcex.resources.Owner`                        |
+------------------------+----------------------------------------------------------+

Security Label Resources
------------------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| SecurityLabel          | :py:class:`~tcex.resources.SecurityLabel`                |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`security_label_examples`

Tag Resources
---------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Tag                    | :py:class:`~tcex.resources.Tag`                          |
+------------------------+----------------------------------------------------------+

Examples
~~~~~~~~
:ref:`tag_examples`

Task Resources
--------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Task                   | :py:class:`~tcex.resources.Task`                         |
+------------------------+----------------------------------------------------------+

Victim Resources
----------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Victim                 | :py:class:`~tcex.resources.Victim`                       |
+------------------------+----------------------------------------------------------+

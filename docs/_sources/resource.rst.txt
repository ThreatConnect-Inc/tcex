.. include:: <isonum.txt>
.. _resources:

==========
Resources
==========

The ThreatConnect |trade| TcEx Framework provides access to the ThreatConnect API using the :py:mod:`~tcex.tcex_resources` module.  The Resource Classes can be accessed via the ``tcex.resources`` property of the TcEx Framework.

**Direct Access**

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 3-4

    tcex = TcEx()

    resource = tcex.resources.Adversary(tcex)
    results = resource.request()

    print(resource['status'])
    print(resource['data'])

    tcex.exit()

**Dynamic Access**

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 3-4

    tcex = TcEx()

    resource = getattr(tcex.resources, tcex.safe_rt('User Agent'))(tcex)
    results = resource.request()

    print(resource['status'])
    print(resource['data'])

    tcex.exit()


Group Resources
-------------------

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

.. Note:: Custom Indicators can be accessed by the **Type**. The ThreatConnect platform supports Custom indicator types with a space in the name. To prevent issues with the space all Custom Resource (Indicator) types should be made **safe** by using the :py:meth:`~tcex.tcex.TcEx.safe_rt` method.

Owner Resources
-------------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Owner                  | :py:class:`~tcex.tcex_resources.Owner`                   |
+------------------------+----------------------------------------------------------+

Task Resources
-------------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Task                   | :py:class:`~tcex.tcex_resources.Task`                    |
+------------------------+----------------------------------------------------------+

Victim Resources
-------------------

+------------------------+----------------------------------------------------------+
| Resource Type          | Class                                                    |
+========================+==========================================================+
| Victim                 | :py:class:`~tcex.tcex_resources.Victim`                  |
+------------------------+----------------------------------------------------------+
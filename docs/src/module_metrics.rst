.. include:: <isonum.txt>
.. _module_metrics:

================
Module: Metrics
================
The ThreatConnect TcEx App Framework provides a simple interface for creating and adding Metrics in Apps.  The :py:mod:`~tcex.tcex_metrics_v2.TcExMetricsV2` module will automatically create the Metric if it does not already exist in ThreatConnect.  The Metric Name is a unique field in the ThreatConnect platform. For more information on ThreatConnect Metrics, see the documents at https://docs.threatconnect.com/en/latest/rest_api/custom_metrics/custom_metrics.html#custom-metrics.

Metrics Instance
================
The ``tcex.metrics()`` method has required fields of **name**, **description**, **data_type**, **interval**, and **keyed** as parameters.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    metrics = tcex.metric('My Metrics', 'Metric Testing', 'Sum', 'Daily', False)

Add Metrics
===========
The :py:meth:`~tcex.tcex_metrics_v2.TcExMetricsV2.add` method has a required field of **value**. It also accepts an option field for **date**, **return_value**, and **key**.  If no date is provided, the current **datetime** will be used.  The **return_value** field will tell the API to return the value for the current interval.  The **key** arg is only used for Keyed Metrics; otehrwise, the :py:meth:`~tcex.tcex_metrics_v2.TcExMetricsV2.add_keyed` method can be used.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    metrics = tcex.metric('My Metric', 'TcEx Metric Testing', 'Sum', 'Daily', False)
    metrics.add(123)

Add Keyed Metrics
=================
The :py:meth:`~tcex.tcex_metrics_v2.TcExMetricsV2.add_keyed` method has required fields of **value** and **key**. It also accepts option fields for **date** and **return_value**.  If no date is provided the current **datetime** will be used.  The **return_value** field will tell the API to return the value for the current interval.

.. code-block:: python
    :linenos:
    :lineno-start: 1

    metrics = tcex.metric('My Keyed Metric', 'TcEx Keyed Metric Testing', 'Sum', 'Daily', True)
    address_results = metrics.add(100, key='Address', date='2019-03-28T12:25:40Z', return_value=True)
    host_results = metrics.add(99, 'Host', '2019-03-28T12:25:40Z', True)

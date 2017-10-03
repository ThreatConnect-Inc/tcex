.. _resources_custom_metrics:

.. Note:: Available in 5.4+ version of the ThreatConnect API.

+ Direct Access: ``resource = tcex.resources.CustomMetric(tcex)``
+ Dynamic Access: ``resource = tcex.resource('CustomMetric')``

Read Metric Configs
===================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14-15

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('CustomMetric')
        results = resource.request()
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
      "status": "Success",
      "data": {
        "resultCount": 3,
        "customMetricConfig": [
          {
            "id": 2,
            "name": "Block Firewall Playbook Executions",
            "dataType": "Sum",
            "interval": "Hourly",
            "keyedValues": false,
            "description": "Execution count for HTTP trigger on Block Firewall"
          },
          {
            "id": 3,
            "name": "My Custom Metric",
            "dataType": "Sum",
            "interval": "Hourly",
            "keyedValues": true,
            "description": "A sum of all occurrences per Indicator Source"
          }
        ]
      }
    }

Create Metric Config
====================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14-22

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('CustomMetric')
        resource.http_method = 'POST'
        body = {
          'name': 'My Custom Metric',
          'dataType': 'Sum',
          'interval': 'Hourly',
          'keyedValues': true,
          'description': 'A sum of all occurrences per Indicator Source'
        }
        results = resource.request()
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
      "status": "Success",
      "data": {
        "customMetricConfig": {
          "id": 3,
          "name": "My Custom Metric",
          "dataType": "Sum",
          "interval": "Hourly",
          "keyedValues": true,
          "description": "A sum of all occurrences per Indicator Source"
        }
      }
    }

Read Metric Config (by ID)
==========================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14-16

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('CustomMetric')
        resource.resource_id(3)
        results = resource.request()
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
      "status": "Success",
      "data": {
        "customMetricConfig": {
          "id": 3,
          "name": "My Custom Metric",
          "dataType": "Sum",
          "interval": "Hourly",
          "keyedValues": true,
          "description": "A sum of all occurrences per Indicator Source"
        }
      }
    }

Read Metric Config (by Name)
============================

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14-16

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('CustomMetric')
        resource.resource_name('My Custom Metric')
        results = resource.request()
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
      "status": "Success",
      "data": {
        "customMetricConfig": {
          "id": 3,
          "name": "My Custom Metric",
          "dataType": "Sum",
          "interval": "Hourly",
          "keyedValues": true,
          "description": "A sum of all occurrences per Indicator Source"
        }
      }
    }

Update Metric Config
====================

.. Note:: Both the Metric ID and Metric Name can be used via the ``resource_id()`` or ``resource_name`` methods.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14-16

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('CustomMetric')
        resource.resource_id(3)
        resource.http_method = PUT
        body = {
          'name': 'My Custom Metric',
          'dataType': 'Sum',
          'interval': 'Hourly',
          'keyedValues': true,
          'description': '(updated) A sum of all occurrences per Indicator Source'
        }
        results = resource.request()
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
      "status": "Success",
      "data": {
        "customMetricConfig": {
          "id": 3,
          "name": "My Custom Metric",
          "dataType": "Sum",
          "interval": "Hourly",
          "keyedValues": true,
          "description": "(updated) A sum of all occurrences per Indicator Source"
        }
      }
    }

Create Metric Data
==================

.. Note:: The weight parameter is optional.

.. Important:: Creating metrics will return a 204 by default with no Data.  To get updated Metrics
          use the returnValue=true query parameter.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14-18,20-21

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('CustomMetric')
        resource.http_method = 'POST'
        resource.data(3)
        body = {
          "value": 1,
          "weight": 1
        }
        resource.body = json.dumps(body)
        results = resource.request()
        print(results.get('status_code'))


    if __name__ == "__main__":
        main()

Response
--------

No response returned.

Create Metric Data (with returnValue)
=====================================

.. Note:: The weight parameter is optional.

.. code-block:: python
    :linenos:
    :lineno-start: 1
    :emphasize-lines: 14-19,20-21

    """ standard """
    import json
    from datetime import datetime
    """ third party """
    """ custom """
    from tcex import TcEx

    tcex = TcEx()
    args = tcex.args


    def main():
        """ """
        resource = tcex.resource('CustomMetric')
        resource.http_method = 'POST'
        resource.data(3, True)
        body = {
          "name": "blue",
          "value": 1,
          "weight": 1
        }
        results = resource.request()
        print(json.dumps(results.get('data'), indent=4))


    if __name__ == "__main__":
        main()

Response
--------
The response contains the processed results for the reporting period.  For example if the Metric configured for a sum over a 1 hour period and this was the second value of **1** posted the response value would be **2**.

.. code-block:: javascript
    :linenos:
    :lineno-start: 1

    {
        "value": 2,
        "date": "2017-10-02T20:00:00-04:00"
    }
# -*- coding: utf-8 -*-
""" TcEx Metrics Module """


class TcExMetricsV2(object):
    """TcEx Metrics Class"""

    def __init__(self, tcex, name, description, data_type, interval, keyed=False):
        """Initialize the Class properties.

        Args:
            name (str): The name for the metric.
            description (str): The description of the metric.
            data_type (str): The type of metric: Sum, Count, Min, Max, First, Last, and Average.
            interval (str): The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly.
            keyed (bool, default:False): Indicates whether the data will have a keyed value.
        """
        self.tcex = tcex
        self._metric_data_type = data_type
        self._metric_description = description
        self._metric_id = None
        self._metric_interval = interval
        self._metric_keyed = keyed
        self._metric_name = name

        if not self.metric_find():
            self.metric_create()

    def metric_create(self):
        """Create the defined metric.

        .. code-block:: javascript

            {
                "status": "Success",
                "data": {
                    "customMetricConfig": {
                        "id": 12,
                        "name": "Added Reports",
                        "dataType": "Sum",
                        "interval": "Daily",
                        "keyedValues": false,
                        "description": "Added reports daily count."
                    }
                }
            }
        """
        body = {
            'dataType' : self._metric_data_type,
            'description' : self._metric_description,
            'interval' : self._metric_interval,
            'name' : self._metric_name,
            'keyedValues' : self._metric_keyed
        }
        self.tcex.log.debug('metric body: {}'.format(body))
        r = self.tcex.session.post('/v2/customMetrics', json=body)

        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.tcex.handle_error(700, [r.status_code, r.text])

        data = r.json()
        self._metric_id = data.get('data', {}).get('customMetricConfig', {}).get('id')
        self.tcex.log.debug('metric data: {}'.format(data))

    def metric_find(self):
        """Find the Metric by name.

        .. code-block:: javascript

            {
                "status": "Success",
                "data": {
                    "resultCount": 1,
                    "customMetricConfig": [
                        {
                            "id": 9,
                            "name": "My Metric",
                            "dataType": "Sum",
                            "interval": "Daily",
                            "keyedValues": false,
                            "description": "TcEx Metric Testing"
                        }
                    ]
                }
            }
        """
        params = {
            'resultLimit': 50,
            'resultStart': 0
        }
        while True:
            if params.get('resultStart') >= params.get('resultLimit'):
                break
            r = self.tcex.session.get('/v2/customMetrics', params=params)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.tcex.handle_error(705, [r.status_code, r.text])
            data = r.json()
            for metric in data.get('data', {}).get('customMetricConfig'):
                if metric.get('name') == self._metric_name:
                    self._metric_id = metric.get('id')
                    info = 'found metric with name "{}" and Id {}.'
                    self.tcex.log.info(info.format(self._metric_name, self._metric_id))
                    return True
            params['resultStart'] += params.get('resultLimit')
        return False

    def add(self, value, date=None, return_value=False, key=None):
        """Add metrics data to collection.

        Args:
            value (str): The value of the metric.
            date (str, optional): The optional date of the metric.
            return_value (bool, default:False): Tell the API to return the updates metric value.
            key (str, optional): The key value for keyed metrics.

        Return:
            dict: If return_value is True a dict with the current value for the time period
                is returned.
        """
        data = {}
        if self._metric_id is None:
            self.tcex.handle_error(715, [self._metric_name])

        body = {'value': value}
        if date is not None:
            body['date'] = self.tcex.utils.format_datetime(date, date_format='%Y-%m-%dT%H:%M:%SZ')
        if key is not None:
            body['name'] = key
        self.tcex.log.debug('metric data: {}'.format(body))
        params = {}
        if return_value:
            params = {'returnValue': 'true'}
        url = '/v2/customMetrics/{}/data'.format(self._metric_id)
        r = self.tcex.session.post(url, json=body, params=params)
        if r.status_code == 200 and 'application/json' in r.headers.get('content-type', ''):
            data = r.json()
        elif r.status_code == 204:
            pass
        else:
            self.tcex.handle_error(710, [r.status_code, r.text])

        return data

    def add_keyed(self, value, key, date=None, return_value=False):
        """Add keyed metrics data to collection.

        Args:
            value (str): The value of the metric.
            key (str): The key value for keyed metrics.
            date (str, optional): The optional date of the metric.
            return_value (bool, default:False): Tell the API to return the updates metric value.

        Return:
            dict: If return_value is True a dict with the current value for the time period
                is returned.
        """
        return self.add(value, date, return_value, key)

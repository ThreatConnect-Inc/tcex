# -*- coding: utf-8 -*-
""" TcEx Metrics Module """
import json

class TcExMetricsV2(object):
    """TcEx Metrics Class."""

    def __init__(self, tcex, name, description, data_type, interval, keyed=False):
        """ Initialize class properties

        Args:
            name: The name for the metric.
            description: The description of the metric.
            data_type: The type of metric: Sum, Count, Min, Max, First, Last, and Average
            interval: The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly
            keyed: Indicates whether the data will have a keyed value.
        """
        self._tcex = tcex
        self._metric_data_type = data_type
        self._metric_description = description
        self._metric_id = None
        self._metric_interval = interval
        self._metric_keyed = keyed
        self._metric_name = name

        if not self.metric_find():
            self.metric_create()

    # @property
    # def metric_exists(self):
    #     """ Validate that the metric Id provided is still valid
    #     """
    #     if self._metric_id is not None:
    #         resource = self.metric_resource
    #         resource.metric_id(self._metric_id)
    #         results = resource.request()
    #         if results.get('response').status_code == 200:
    #             return True
    #     return False

    @property
    def metric_resource(self):
        """ Return metric resource """
        return self._tcex.resource('CustomMetric')

    def metric_create(self):
        """Create the defined metric
        """
        resource = self.metric_resource
        resource.http_method = 'POST'
        body = {
            'dataType' : self._metric_data_type,
            'description' : self._metric_description,
            'interval' : self._metric_interval,
            'name' : self._metric_name,
            'keyedValues' : self._metric_keyed
        }
        self._tcex.log.debug('metric body: {}'.format(json.dumps(body)))
        resource.body = json.dumps(body)
        results = resource.request()

        if results.get('status') == 'Success':
            self._metric_id = results.get('data', {}).get('id')
            self._tcex.log.debug('metric data: {}'.format(results.get('data')))
            self._tcex.log.debug('metric id: {}'.format(self._metric_id))
        else:
            err = u'Failed to add metric ({})'.format(results.get('response').text)
            self._tcex.log.error(err)
            raise RuntimeError(err)

    def metric_find(self):
        """Report Metrics"""
        resource = self.metric_resource
        for results in resource:
            if results.get('status') != 'Success':
                err = 'Error during while retrieving metrics.'
                self._tcex.log.error(err)
                continue

            for metric in results.get('data'):
                if metric.get('name') == self._metric_name:
                    self._metric_id = metric.get('id')
                    info = 'found metric with name "{}" and Id {}.'
                    self._tcex.log.info(info.format(self._metric_name, self._metric_id))
                    return True

        return False

    def add(self, value, date=None, return_value=False, key=None):
        """Add Metrics

        Args:
            value: The value of the metric.
            date: The optional date of the metric.
            return_value: Tell the API to return the updates metric value.
            key: The key value for keyed metrics.

        Return:
            (None|Dict): A None value if return value was not requested or a dict.
        """
        response = None
        if self._metric_id is None:
            err = 'No metric ID found for "{}".'.format(self._metric_name)
            self._tcex.log.error(err)
            raise RuntimeError(err)
        resource = self.metric_resource
        resource.http_method = 'POST'
        if return_value:
            resource.add_payload('returnValue', 'true')
        resource.data(self._metric_id)
        body = {
            'value': value
        }
        if date is not None:
            body['date'] = date
        if key is not None:
            body['name'] = key
        self._tcex.log.debug('metric data: {}'.format(json.dumps(body)))
        resource.body = json.dumps(body)
        results = resource.request()

        if results.get('response').status_code == 200:
            response = results.get('response').json()
        elif results.get('response').status_code == 204:
            pass
        else:
            err = u'Failed to add metric ({})'.format(results.get('response').text)
            self._tcex.log.error(err)
            self._tcex.message_tc(err)
            raise RuntimeError(err)

        return response

    def add_keyed(self, value, key, date=None, return_value=False):
        """Add keyed metrics

        Args:
            value: The value of the metric.
            key: The key value for keyed metrics.
            date: The optional date of the metric.
            return_value: Tell the API to return the updates metric value.

        Return:
            (None|Dict): A None value if return value was not requested or a dict.
        """
        return self.add(value, date, return_value, key)

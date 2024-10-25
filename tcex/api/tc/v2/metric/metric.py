"""TcEx Framework Module"""

# standard library
import logging

# third-party
from requests import Session  # TYPE-CHECKING

# first-party
from tcex.exit.error_code import handle_error
from tcex.logger.trace_logger import TraceLogger
from tcex.util import Util

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class Metric:
    """TcEx Metrics Class

    Args:
        session_tc: An configured instance of request.Session with TC API Auth.
        name: The name for the metric.
        description: The description of the metric.
        data_type: The type of metric: Sum, Count, Min, Max, First, Last, and Average.
        interval: The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly.
        keyed: Indicates whether the data will have a keyed value.
    """

    def __init__(
        self,
        session_tc: Session,
        name: str,
        description: str,
        data_type: str,
        interval: str,
        keyed: bool = False,
    ):
        """Initialize the Class properties."""
        self.session_tc = session_tc
        self._metric_data_type = data_type
        self._metric_description = description
        self._metric_interval = interval
        self._metric_keyed = keyed
        self._metric_name = name

        # properties
        self._metric_id = None
        self.log = _logger
        self.util = Util

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
            'dataType': self._metric_data_type,
            'description': self._metric_description,
            'interval': self._metric_interval,
            'name': self._metric_name,
            'keyedValues': self._metric_keyed,
        }
        self.log.debug(f'metric body: {body}')
        r = self.session_tc.post('/v2/customMetrics', json=body)

        if not r.ok:  # pragma: no cover
            handle_error(700, [r.status_code, r.text])

        data = r.json()
        self._metric_id = data.get('data', {}).get('customMetricConfig', {}).get('id')
        self.log.debug(f'metric data: {data}')

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
        params: dict[str, int] = {'resultLimit': 50, 'resultStart': 0}
        while True:
            if params['resultStart'] >= params['resultLimit']:
                break
            r = self.session_tc.get('/v2/customMetrics', params=params)
            if not r.ok:  # pragma: no cover
                handle_error(705, [r.status_code, r.text])
            data = r.json()
            for metric in data.get('data', {}).get('customMetricConfig'):
                if metric.get('name') == self._metric_name:
                    self._metric_id = metric.get('id')
                    self.log.info(
                        f'found metric with name "{self._metric_name}" '
                        f'and Id {self._metric_id}.'
                    )
                    return True
            params['resultStart'] += params['resultLimit']
        return False

    def add(self, value, date=None, return_value=False, key=None, weight=None):
        """Add metric data to collection.

        Args:
            value (str): The value of the metric.
            date (str, optional): The optional date of the metric.
            return_value (bool, default:False): Tell the API to return the updates metric value.
            key (str, optional): The key value for keyed metric.
            weight (str, optional): The weight value (only needed for averages)

        Return:
            dict: If return_value is True a dict with the current value for the time period
                is returned.
        """
        data = {}
        if self._metric_id is None:  # pragma: no cover
            handle_error(715, [self._metric_name])

        body = {'value': value}
        if date is not None:
            body['date'] = self.util.any_to_datetime(date).strftime('%Y-%m-%dT%H:%M:%SZ')

        if key is not None:
            body['name'] = key
        if weight:
            body['weight'] = weight
        self.log.debug(f'metric data: {body}')

        params = {}
        if return_value:
            params = {'returnValue': 'true'}

        url = f'/v2/customMetrics/{self._metric_id}/data'
        r = self.session_tc.post(url, json=body, params=params)
        if r.status_code == 200 and 'application/json' in r.headers.get('content-type', ''):
            data = r.json()
        elif r.status_code == 204:
            pass
        else:  # pragma: no cover
            handle_error(710, [r.status_code, r.text])

        return data

    def add_keyed(self, value, key, date=None, return_value=False, weight=None):
        """Add keyed metric data to collection.

        Args:
            value (str): The value of the metric.
            key (str): The key value for keyed metric.
            date (str, optional): The optional date of the metric.
            return_value (bool, default:False): Tell the API to return the updates metric value.
            weight (str, optional): The weight value (only needed for averages)

        Return:
            dict: If return_value is True a dict with the current value for the time period
                is returned.
        """
        return self.add(value, date, return_value, key, weight)

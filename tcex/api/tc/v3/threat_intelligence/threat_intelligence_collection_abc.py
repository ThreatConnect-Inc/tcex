"""Case Management Collection Abstract Base Class"""
# standard library
import logging
from abc import ABC

# third-party
from requests import Response
from requests.exceptions import ProxyError

# first-party
from tcex.pleb import Event
from tcex.utils import Utils

# from tcex.api.v3.threat_intelligence.group.group import Group

# get tcex logger
logger = logging.getLogger('tcex')


class ThreatIntelligenceCollectionABC(ABC):
    """Case Management Collection Abstract Base Class

    This class is a base class for Case Management collections that use
    multi-inheritance with a pydantic BaseModel class. To ensure
    properties are not added to the model both @property and @setter
    methods are used.
    """

    def __init__(self, session) -> None:
        """Initialize class properties."""
        # properties
        self._session = session
        self.log = logger
        self._utils = Utils()
        self._event = Event()
        self._filter = None
        self._timeout = None
        self._headers = {'content-type': 'application/json'}

    @property
    def _base_filter(self):
        raise NotImplementedError('Child class must implement this method.')

    def __len__(self) -> int:
        """Return the length of the collection."""
        parameters = {'result_limit': 1}
        if self.filter.__str__():
            parameters['tql'] = self.filter.__str__()

        # convert all keys to camel case
        for k, v in list(parameters.items()):
            k = self._utils.snake_to_camel(k)
            parameters[k] = v

        r = self._session.get(
            self._api_endpoint, params=parameters, headers=self._headers
        )
        # TODO: [med] check with core team on discrepency on missing count.
        return r.json().get('count', len(r.json().get('data', [])))

    @property
    def filter(self) -> None:  # pragma: no cover
        """Return filter method."""
        raise NotImplementedError('Child class must implement this method.')

    @property
    def _api_endpoint(self) -> None:  # pragma: no cover
        """Return filter method."""
        raise NotImplementedError('Child class must implement this method.')

    def iterate(self, base_class) -> 'CaseManagementType':
        parameters = {}
        # parameters['fields'] = ['groups', 'indicators', 'tags', 'securityLabels', 'attributes']
        parameters['fields'] = ['groups', 'indicators', 'tags', 'securityLabels']

        if self.filter.__str__():
            parameters['tql'] = self.filter.__str__()

        while True:
            r = None
            try:
                r = self._session.get(
                    self._api_endpoint, params=parameters, headers=self._headers
                )
                self.log.debug(
                    f'Method: ({r.request.method.upper()}), '
                    f'Status Code: {r.status_code}, '
                    f'URl: ({r.url})'
                )
            except (ConnectionError, ProxyError):  # pragma: no cover
                self._event.send(
                    'handle_error',
                    code=951,
                    message_values=[
                        'OPTIONS',
                        407,
                        '{\"message\": \"Connection Error\"}',
                        self._api_endpoint,
                    ],
                )

            if not self.success(r):
                err = r.text or r.reason
                self._event.send(
                    'handle_error',
                    code=950,
                    message_values=[
                        'OPTIONS',
                        r.status_code,
                        f'"message": "{err}"',
                        r.url,
                    ],
                )

            # reset some vars
            parameters = {}

            data = r.json().get('data', [])
            url = r.json().pop('next', None)

            for result in data:
                try:
                    type_ = result.get('type')
                    yield base_class(session=self._session).get(type_)(**result)
                except:
                    yield base_class(session=self._session, **result)

            # break out of pagination if no next url present in results
            if not url:
                break

    @staticmethod
    def success(r: Response) -> bool:
        """Validate the response is valid.

        Args:
            r (requests.response): The response object.

        Returns:
            bool: True if status is "ok"
        """
        status = True
        if r.ok:
            try:
                if r.json().get('status') != 'Success':  # pragma: no cover
                    status = False
            except Exception:  # pragma: no cover
                status = False
        else:
            status = False
        return status

    @property
    def timeout(self) -> int:
        """Return the timeout of the case management object collection."""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        """Set the timeout of the case management object collection."""
        self._timeout = timeout

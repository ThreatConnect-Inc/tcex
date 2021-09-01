"""Case Management Abstract Base Class"""
# standard library
import logging
from abc import ABC
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

# third-party
from requests import Response
from requests.exceptions import ProxyError

# first-party
from tcex.backports import cached_property
from tcex.pleb import Event
from tcex.utils import Utils

# get tcex logger
logger = logging.getLogger('tcex')


class SecurityABC(ABC):
    """Case Management Abstract Base Class

    This class is a base class for Case Management classes that use
    multi-inheritance with a pydantic BaseModel class. To ensure
    properties are not added to the model both @property and @setter
    methods are used.
    """

    def __init__(self, session) -> None:
        """Initialize class properties."""
        self._session = session
        self._log = logger

        # properties
        self._event = Event()
        self._utils = Utils()

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, data):
        if isinstance(data, type(self._model)):
            self._model = data
        else:
            self._model = type(self.model)(**data)

    @property
    def _base_filter(self) -> dict:  # pragma: no cover
        """Return the object as an entity."""
        raise NotImplementedError('Child class must implement this property.')


    def _iterate_over_sublist(self, sublist_type):
        sublist = sublist_type(session=self._session)
        sublist.tql.add_filter(**self._base_filter)
        for item in sublist:
            yield item

    @property
    def available_fields(self) -> List[str]:
        """Return the available query param field names for this object."""
        return [fd.get('name') for fd in self.fields]

    @cached_property
    def fields(self) -> dict:
        """Return the field data for this object."""
        _fields = {}
        r = self._session.options(f'{self._api_endpoint}/fields', params={'show': 'readOnly'})
        if r.ok:
            _fields = r.json()['data']
        return _fields

    # def entity_mapper(self, entity: dict) -> None:  # pragma: no cover
    #     """Stub for entity mapper"""
    #     raise NotImplementedError('Child class must implement this method.')

    def get(
        self,
        all_available_fields: Optional[bool] = False,
        case_management_id: Optional[int] = None,
        params: Optional[dict] = None,
    ) -> 'CaseManagementType':
        """Get the Case Management Object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            all_available_fields: If True all available fields will be returned.
            case_management_id: The id of the case management object to be returned.
            params: Dict of the params to be sent while retrieving the Artifacts objects.
        """
        if params is None:
            params = {}

        # print('\n!!!! params', params)

        # convert all keys to camel case
        for k, v in list(params.items()):
            del params[k]
            k = self._utils.snake_to_camel(k)
            params[k] = v

        cm_id = case_management_id or self.model.id
        url = f'{self._api_endpoint}/{cm_id}'

        # add fields parameter if provided
        if all_available_fields:
            params['fields'] = []
            for field in self.available_fields:
                params['fields'].append(field)

        if not cm_id:  # pragma: no cover
            message = '{"message": "No ID provided.", "status": "Error"}'
            self._event.send('handle_error', code=952, message_values=['GET', '404', message, url])

        r = None
        try:
            r = self._session.get(url, params=params)
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
        self._log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Status Code: {r.status_code}, '
            f'URl: ({r.url})'
        )
        if len(r.content) < 5000:
            self._log.debug(f'response text: {r.text}')
        else:  # pragma: no cover
            self._log.debug('response text: (text to large to log)')
        if not self.success(r):
            err = r.text or r.reason
            if r.status_code == 404:
                self._event.send(
                    'handle_error', code=952, message_values=['GET', r.status_code, err, r.url]
                )
            self._event.send(
                'handle_error', code=951, message_values=['GET', r.status_code, err, r.url]
            )
        self.model = r.json().get('data')
        # print(type(self.model))
        # print(self.model)

        return r

    @staticmethod
    def success(r: Response) -> bool:
        """Validate the response is valid.

        Args:
            r: The response object.

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

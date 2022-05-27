"""Case Management Abstract Base Class"""
# standard library
import logging

# import inspect
# import re
from abc import ABC
from typing import TYPE_CHECKING, Dict, List, Optional, Union

# third-party
from requests import Response
from requests.exceptions import ProxyError, RetryError

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.backports import cached_property
from tcex.exit.error_codes import handle_error
from tcex.utils import Utils

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v3.v3_types import V3Type

# get tcex logger
logger = logging.getLogger('tcex')


class ObjectABC(ABC):
    """Object Abstract Base Class

    This class is a base class for Object classes that use
    multi-inheritance with a pydantic BaseModel class. To ensure
    properties are not added to the model both @property and @setter
    methods are used.
    """

    def __init__(self, session):
        """Initialize class properties."""
        self._session = session

        # properties
        self._parent_data = {}
        self._remove_objects = {
            'associations': [],
            'attributes': [],
            'securityLabels': [],
            'tags': [],
        }
        self.utils = Utils()
        self.log = logger
        self.request = None

        # define/overwritten in child class
        self._model = None
        self._nested_field_name = None
        self._nested_filter = None
        self.type_ = None

    @property
    def _api_endpoint(self) -> dict:  # pragma: no cover
        """Return the type specific API endpoint."""
        raise NotImplementedError('Child class must implement this property.')

    def _calculate_unique_id(self):
        if self.model.id:
            return {'filter': 'id', 'value': self.model.id}

        if hasattr(self.model, 'xid') and self.model.xid:
            return {'filter': 'xid', 'value': self.model.xid}

        if self.type_.lower() in ['indicator']:
            return {'filter': 'summary', 'value': self.model.summary}

        return {}

    def _iterate_over_sublist(self, sublist_type: object) -> 'V3Type':
        """Iterate over any nested collections."""
        sublist = sublist_type(session=self._session)

        # determine the filter type and value based on the available object fields.
        unique_id_data = self._calculate_unique_id()

        # add the filter (e.g., group.has_indicator.id(TqlOperator.EQ, 123)) for the parent object.
        getattr(getattr(sublist.filter, self._nested_filter), unique_id_data.get('filter'))(
            TqlOperator.EQ, unique_id_data.get('value')
        )

        # return the sub object, injecting the parent data
        for obj in sublist:
            obj._parent_data = {
                'api_endpoint': self._api_endpoint,
                'type': self.type_,
                'unique_id': unique_id_data.get('value'),
            }
            yield obj
        self.request = sublist.request

    def _request(
        self,
        method: str,
        url: str,
        body: Optional[Union[bytes, str]] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> 'Response':
        """Handle standard request with error checking."""
        try:
            self.request = self._session.request(
                method, url, data=body, headers=headers, params=params
            )
            self.log.debug(f'feature=api-tc-v3, request-body={self.request.request.body}')
        except (ConnectionError, ProxyError, RetryError):  # pragma: no cover
            handle_error(
                code=951,
                message_values=[
                    method.upper(),
                    None,
                    '{\"message\": \"Connection/Proxy Error/Retry\"}',
                    url,
                ],
            )

        content_type = self.request.headers.get('Content-Type')
        if content_type == 'application/json' and not self.success(self.request):
            err = self.request.text or self.request.reason
            handle_error(
                code=952,
                message_values=[
                    self.request.request.method.upper(),
                    self.request.status_code,
                    err,
                    self.request.url,
                ],
            )

        # log content for debugging
        if content_type == 'application/json':
            self.log_response_text(self.request)

    @staticmethod
    def _validate_id(id_: int, url: str):
        """Raise exception is id is not provided."""
        if not id_:  # pragma: no cover
            message = '{"message": "No ID provided.", "status": "Error"}'
            handle_error(code=952, message_values=['GET', '404', message, url])

    @property
    def as_entity(self) -> Dict[str, str]:  # pragma: no cover
        """Return the entity representation of the object."""
        raise NotImplementedError('Child class must implement this property.')

    @property
    def available_fields(self) -> List[str]:
        """Return the available query param field names for this object."""
        return [fd.get('name') for fd in self.fields]

    def create(self, params: Optional[dict] = None) -> 'Response':
        """Create or Update the Case Management object.

        This is determined based on if the id is already present in the object.
        """
        method = 'POST'
        body = self.model.gen_body_json(method=method)
        self._request(
            method,
            self.url(method),
            body,
            headers={'content-type': 'application/json'},
            params=params,
        )

        # get the response data from nested data object or full response
        response_json = self.request.json()

        # update the model with the response from the API
        self.model = type(self.model)(**response_json.get('data'))

        return self.request

    def delete(self, params: Optional[dict] = None):
        """Delete the object."""
        method = 'DELETE'
        body = self.model.gen_body_json(method)

        # get the unique id value for id, xid, summary, etc ...
        unique_id = self._calculate_unique_id().get('value')

        # validate an id is available
        self._validate_id(unique_id, self.url(method, unique_id))

        self._request(method, self.url(method, unique_id), body, params=params)

        return self.request

    @cached_property
    def fields(self) -> Dict[str, str]:
        """Return the field data for this object."""
        _fields = {}
        r = self._session.options(f'{self._api_endpoint}/fields', params={})
        if r.ok:
            _fields = r.json().get('data', {})
        return _fields

    def gen_params(self, params: List[dict]) -> List[dict]:
        """Return appropriate params values."""
        # convert all keys to camel case
        params = {self.utils.snake_to_camel(k): v for k, v in params.items()}

        # special parameter for indicators to enable the return the the indicator fields
        # (value1, value2, value3) on std-custom/custom-custom indicator types.
        if self.type_ == 'Indicator':
            params.setdefault('fields', []).append('genericCustomIndicatorValues')

        # add fields parameter if provided
        if '_all_' in params.get('fields', []):
            params['fields'] = list(self.available_fields)

        return params

    def get(
        self,
        object_id: Optional[int] = None,
        params: Optional[dict] = None,
    ) -> 'V3Type':
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
            object_id: The unique id of the object to be returned.
            params: Dict of the params to be sent while retrieving the Artifacts objects.
        """
        method = 'GET'
        object_id = object_id or self.model.id
        params = params or {}

        # get the unique id value for id, xid, summary, etc ...
        unique_id = self._calculate_unique_id().get('value')

        # validate an id is available
        self._validate_id(unique_id, self.url(method, unique_id))

        body = self.model.gen_body_json(method)
        params = self.gen_params(params)
        self._request(method, self.url(method, unique_id), body, params)

        # update model
        self.model = self.request.json().get('data')

        return self.request

    def log_response_text(self, response: Response):
        """Log the response text."""
        response_text = 'response text: (text to large to log)'
        if len(response.content) < 5000:  # check size of content for performance
            response_text = response.text
        self.log.debug(f'feature=api-tc-v3, response-body={response_text}')

    @property
    def model(self) -> 'V3Type':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['V3Type', dict]):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    @cached_property
    def properties(self) -> dict:
        """Return defined API properties for the current object.

        This property is used in testing API consistency.
        """
        _properties = []
        try:
            r = self._session.options(
                self._api_endpoint,
                params={'show': 'readOnly'},
                headers={'content-type': 'application/json'},
            )
            if r.ok:
                _properties = r.json()
        except (ConnectionError, ProxyError):
            handle_error(
                code=951,
                message_values=[
                    'OPTIONS',
                    407,
                    '{\"message\": \"Connection Error\"}',
                    self._api_endpoint,
                ],
            )
        return _properties

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

    def update(self, mode: Optional[str] = None, params: Optional[dict] = None) -> 'Response':
        """Create or Update the Case Management object.

        This is determined based on if the id is already present in the object.
        """
        method = 'PUT'
        body = self.model.gen_body_json(method=method, mode=mode)

        # get the unique id value for id, xid, summary, etc ...
        unique_id = self._calculate_unique_id().get('value')

        # validate an id is available
        self._validate_id(unique_id, self.url(method))

        self._request(
            method,
            self.url(method, unique_id=unique_id),
            body,
            headers={'content-type': 'application/json'},
            params=params,
        )

        # get the response data from nested data object or full response
        response_json = self.request.json()

        self.model = type(self.model)(**response_json.get('data'))

        return self.request

    def url(self, method: str, unique_id: Optional[str] = None) -> str:
        """Return the proper URL."""
        unique_id = unique_id or self.model.id
        if method in ['DELETE', 'GET', 'PUT']:
            return f'{self._api_endpoint}/{unique_id}'
        return self._api_endpoint

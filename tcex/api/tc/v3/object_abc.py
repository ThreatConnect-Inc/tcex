"""TcEx Framework Module"""

# standard library
import logging
from abc import ABC
from collections.abc import Generator
from typing import Self

# third-party
from requests import Response, Session
from requests.exceptions import ProxyError, RetryError

# first-party
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.exit.error_code import handle_error
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property
from tcex.util import Util

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class ObjectABC(ABC):
    """Object Abstract Base Class

    This class is a base class for Object classes that use
    multi-inheritance with a pydantic BaseModel class. To ensure
    properties are not added to the model both @property and @setter
    methods are used.
    """

    def __init__(self, session: Session):
        """Initialize instance properties."""
        self._session: Session = session

        # properties
        self._parent_data = {}
        self._remove_objects = {
            'associations': [],
            'attributes': [],
            'securityLabels': [],
            'tags': [],
        }
        self.util = Util()
        self.log = _logger
        self.request: Response

        # define/overwritten in child class
        self._model: V3ModelABC
        self._nested_field_name: str | None = None
        self._nested_filter: str | None = None
        self.type_: str

    @property
    def _api_endpoint(self) -> str:  # pragma: no cover
        """Return the type specific API endpoint."""
        raise NotImplementedError('Child class must implement this property.')

    def _calculate_unique_id(self) -> dict[str, int | str]:
        if self.model.id:
            return {'filter': 'id', 'value': self.model.id}

        if hasattr(self.model, 'xid') and self.model.xid:  # type: ignore
            return {'filter': 'xid', 'value': self.model.xid}  # type: ignore

        if self.type_.lower() in ['indicator']:
            return {'filter': 'summary', 'value': self.model.summary}  # type: ignore

        return {}

    def _iterate_over_sublist(
        self, sublist_type: ObjectCollectionABC, custom_associations: bool = False
    ) -> Generator[Self, None, None]:
        """Iterate over any nested collections."""
        sublist = sublist_type(session=self._session)  # type: ignore

        # determine the filter type and value based on the available object fields.
        unique_id_data = self._calculate_unique_id()

        # id!=2984993+AND+hasGroup(typename="all"+AND+isGroup+=+false+AND+hasIndicator(id=2984993))
        # add the filter (e.g., group.has_indicator.id(TqlOperator.EQ, 123)) for the parent object.
        if custom_associations is True:
            sublist.filter.tql = (
                'id!={id} AND hasGroup(typename="all" '
                'AND isGroup = false AND hasIndicator(id={id}))'
            ).format(id=self.model.id)
            sublist.params = {'fields': ['associationName']}
        else:
            getattr(
                getattr(sublist.filter, self._nested_filter),  # type: ignore
                unique_id_data.get('filter'),  # type: ignore
            )(TqlOperator.EQ, unique_id_data.get('value'))

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
        body: bytes | str | None = None,
        params: dict | None = None,
        headers: dict | None = None,
    ):
        """Handle standard request with error checking."""
        try:
            self.request = self._session.request(
                method, url, data=body, headers=headers, params=params
            )
            if isinstance(self.request.request.body, str) and len(self.request.request.body) < 1000:
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
                    (self.request.request.method or '').upper(),
                    self.request.status_code,
                    err,
                    self.request.url,
                ],
            )

        # log content for debugging
        if content_type == 'application/json':
            self.log_response_text(self.request)

    @staticmethod
    def _validate_id(id_: int | str | None, url: str):
        """Raise exception is id is not provided."""
        if not id_:  # pragma: no cover
            message = '{"message": "No ID provided.", "status": "Error"}'
            handle_error(code=952, message_values=['GET', '404', message, url])

    @property
    def as_entity(self) -> dict[str, str]:  # pragma: no cover
        """Return the entity representation of the object."""
        raise NotImplementedError('Child class must implement this property.')

    @property
    def available_fields(self) -> list[str]:
        """Return the available query param field names for this object."""
        return [fd['name'] for fd in self.fields]

    def create(self, params: dict | None = None) -> Response:
        """Create or Update the Case Management object.

        This is determined based on if the id is already present in the object.
        """
        method = 'POST'
        body = self.model.gen_body_json(method=method)
        params = self.gen_params(params) if params else None
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

    def delete(self, params: dict | None = None):
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
    def fields(self) -> list[dict[str, str]]:
        """Return the field data for this object."""
        _fields = []
        r = self._session.options(f'{self._api_endpoint}/fields', params={})
        if r.ok:
            _fields = r.json().get('data', [])
        return _fields

    def gen_params(self, params: dict) -> dict:
        """Return appropriate params values."""
        # convert all keys to camel case
        params = {self.util.snake_to_camel(k): v for k, v in params.items()}

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
        object_id: int | None = None,
        params: dict | None = None,
    ) -> Response:
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
        params = self.gen_params(params) if params else None

        # get the unique id value for id, xid, summary, etc ...
        unique_id = self._calculate_unique_id().get('value')

        # validate an id is available
        self._validate_id(unique_id, self.url(method, unique_id))

        body = self.model.gen_body_json(method)
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
    def model(self) -> V3ModelABC:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | V3ModelABC):
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
    def properties(self) -> dict[str, dict | list]:
        """Return defined API properties for the current object.

        This property is used in testing API consistency.
        """
        _properties = {}
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

    def update(self, mode: str | None = None, params: dict | None = None) -> Response:
        """Create or Update the Case Management object.

        This is determined based on if the id is already present in the object.
        """
        method = 'PUT'
        body = self.model.gen_body_json(method=method, mode=mode)
        params = self.gen_params(params) if params else None

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

    def url(self, method: str, unique_id: int | str | None = None) -> str:
        """Return the proper URL."""
        unique_id = unique_id or self._calculate_unique_id().get('value')
        if method in ['DELETE', 'GET', 'PUT']:
            return f'{self._api_endpoint}/{unique_id}'
        return self._api_endpoint

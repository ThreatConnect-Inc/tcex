"""Case Management Abstract Base Class"""
# standard library
import logging

# import inspect
# import re
from abc import ABC
from typing import TYPE_CHECKING, Dict, List, Optional, Union

# third-party
from requests import Response
from requests.exceptions import ProxyError

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

    def __init__(self, session) -> None:
        """Initialize class properties."""
        self._session = session

        # properties
        self._model = None  # defined in child class
        self._nested_filter = None  # defined in child class
        self._parent_remove_objects = None  # set by _iterate_over_sublist
        self._remove_objects = {
            'associations': [],
            'attributes': [],
            'securityLabels': [],
            'tags': [],
        }
        self._utils = Utils()
        self.log = logger
        self.request = None
        self.type_ = None  # defined in child class

    @property
    def _api_endpoint(self) -> dict:  # pragma: no cover
        """Return the type specific API endpoint."""
        raise NotImplementedError('Child class must implement this property.')

    def _iterate_over_sublist(self, sublist_type: object) -> 'V3Type':
        """Iterate over any nested collections."""
        sublist = sublist_type(session=self._session)
        # add the filter (e.g., group.has_indicator.id(TqlOperator.EQ, 123)) for the parent object.
        getattr(sublist.filter, self._nested_filter).id(TqlOperator.EQ, self.model.id)
        # yield from sublist
        for obj in sublist:
            obj._parent_remove_objects = self._remove_objects
            yield obj

    def _request(
        self,
        method: str,
        url: str,
        body: Optional[Union[bytes, str]],
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Response:
        """Handle standard request with error checking."""
        _request = None
        try:
            if body:
                headers = headers or {}
                if 'content-type' not in (header.lower() for header in headers.keys()):
                    headers['content-type'] = 'application/json'

            _request = self._session.request(method, url, data=body, headers=headers, params=params)
            # log content for debugging
            self.log.debug(
                f'action=submit, method={_request.request.method}, '
                f'url={_request.request.url}, '
                f'status_code={_request.status_code}, '
                f'body={_request.request.body}'
            )
        except (ConnectionError, ProxyError):  # pragma: no cover
            handle_error(
                code=951,
                message_values=[
                    _request.request.method.upper(),
                    _request.status_code,
                    '{\"message\": \"Connection/Proxy Error\"}',
                    url,
                ],
            )

        if not self.success(_request):
            err = _request.text or _request.reason
            handle_error(
                code=952,
                message_values=[
                    _request.request.method.upper(),
                    _request.status_code,
                    err,
                    _request.url,
                ],
            )

        # log content for debugging
        self.log_response_text(_request)

        return _request

    @staticmethod
    def _validate_id(id_: int, url: str) -> None:
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

    def delete(self) -> None:
        """Delete the object."""
        method = 'DELETE'
        body = self.model.gen_body(method)

        # validate an id is available
        self._validate_id(self.model.id, self.url(method))

        self.request = self._request(method, self.url(method), body)

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
        params = {self._utils.snake_to_camel(k): v for k, v in params.items()}

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

        # validate an id is available
        self._validate_id(self.model.id, self.url(method))

        body = self.model.gen_body(method)
        params = self.gen_params(params)
        self.request = self._request(method, self.url(method), body, params)

        # update model
        self.model = self.request.json().get('data')

        return self.request

    def log_response_text(self, response: Response) -> None:
        """Log the response text."""
        response_text = 'response text: (text to large to log)'
        if len(response.content) < 5000:  # check size of content for performance
            response_text = response.text
        self.log.debug(f'response text: {response_text}')

    @property
    def model(self) -> 'V3Type':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['V3Type', dict]) -> None:
        """Create model using the provided data."""
        if isinstance(data, type(self._model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        # TODO: [med] @bpurdy - should we raise an exception if the wrong data type is provided?

    # @property
    # def post_properties(self) -> List[str]:
    #     """Return all the properties available in POST requests."""
    #     post_properties = []
    #     for p, pd in sorted(self.properties.items()):
    #         read_only = pd.get('read-only', False)
    #         if not read_only:
    #             post_properties.append(p)

    #     return post_properties

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

    # @property
    # def put_properties(self) -> List[str]:
    #     """Return all the properties available in PUT requests."""
    #     put_properties = []
    #     for p, pd in sorted(self.properties.items()):
    #         # get read-only value for display and required value
    #         updatable = pd.get('updatable', True)
    #         read_only = pd.get('read-only', False)
    #         if not read_only:
    #             if updatable:
    #                 put_properties.append(p)

    #     return put_properties

    # @property
    # def required_properties(self) -> List[str]:
    #     """Return a list of required fields for current object."""
    #     rp = []
    #     for p, pd in self.properties.items():
    #         if pd.get('required'):
    #             rp.append(p)
    #     return rp

    def remove(self):
        """Remove the tag from the parent object."""
        self._parent_remove_objects['tags'].append(self.model.id)

    def submit(self, mode: Optional[str] = None) -> Response:
        """Create or Update the Case Management object.

        This is determined based on if the id is already present in the object.
        """
        method = 'PUT' if self.model.id else 'POST'
        body = self.model.gen_body(method=method, mode=mode)
        self.request: Response = self._request(
            method, self.url(method), body, headers={'content-type': 'application/json'}
        )

        # get the response data from nested data object or full response
        response_json = self.request.json()

        # TODO: [high] Unsure if the entire model should be reset or just the id.
        #     If entire model the inner objects get ids set which is nice.
        new_id = response_json.get('data', response_json).get('id')
        if new_id:
            self.model.id = new_id

        return self.request

    # def submit_mode_delete(self) -> Response:
    #     """Submit metadata removal."""
    #     method = 'PUT'
    #     body = {}
    #     # self._remove_objects = {
    #     #     'associations': [],
    #     #     'attributes': [],
    #     #     'securityLabels': [],
    #     #     'tags': [],
    #     # }

    #     # What does this look like?
    #     #
    #     #
    #     #
    #     #
    #     #

    #     # for type_, data in self._remove_objects.items():

    #     # self.request: Response = self._request(
    #     #     method, self.url(method), body, headers={'content-type': 'application/json'}
    #     # )

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

    def url(self, method: str) -> str:
        """Return the proper URL."""
        if method in ['DELETE', 'GET', 'PUT']:
            return f'{self._api_endpoint}/{self.model.id}'
        return self._api_endpoint

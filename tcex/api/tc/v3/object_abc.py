"""Case Management Abstract Base Class"""
# standard library
import logging

# import inspect
# import re
from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

# third-party
from requests import Response
from requests.exceptions import ProxyError

# first-party
from tcex.backports import cached_property
from tcex.pleb.registry import registry
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
        self.type_ = None  # defined in child class
        self._utils = Utils()
        self.log = logger
        self.request = None

    @property
    def _api_endpoint(self) -> dict:  # pragma: no cover
        """Return the type specific API endpoint."""
        raise NotImplementedError('Child class must implement this property.')

    @property
    def _base_filter(self) -> dict:  # pragma: no cover
        """Return the object as an entity."""
        raise NotImplementedError('Child class must implement this property.')

    @staticmethod
    def _schema_properties(schema: dict, ref: str) -> dict:
        """Return the schema properties for the ref."""
        return schema.get('definitions', {}).get(ref, {}).get('properties', {})

    @staticmethod
    def _schema_refs(attribute_property: dict) -> List[str]:
        """Return one or more ref values from a property."""
        refs = []

        # get allOf ref or refs
        for all_of in attribute_property.get('allOf', []):
            refs.append(all_of.get('$ref'))

        # get anyOf ref or refs
        for any_of in attribute_property.get('anyOf', []):
            refs.append(any_of.get('$ref'))

        # get data item ref
        ref = attribute_property.get('data', attribute_property).get('items', {}).get('$ref')
        if ref is not None:
            refs.append(ref)

        return refs

    def _generate_body(self, method: str) -> dict:
        """Return the generated POST body."""
        schema = self.model.schema(ref_template='{model}')
        properties = self._schema_properties(schema, schema.get('$ref'))
        raw_body = self.model.dict(by_alias=True, exclude_none=True)
        return self._generate_body_filtered(schema, method, properties, raw_body)

    def _generate_body_filtered(
        self, schema: dict, method: str, properties: dict, body: Any, nested: Optional[str] = None
    ) -> dict:
        """Return body with null, read-only, and not updatable fields removed.

        This method is called recursively to resolve all nested models.
        """
        if isinstance(body, dict):
            safe_data = body.copy()  # make a copy of the original
            _filtered_body = {}

            # iterate over body model: k is JSON key and v is array/dict/str/model
            for k, v in safe_data.items():
                # get the type of model for the key (e.g., "note" -> NoteModel)
                nested_schema = properties.get(k)

                # skip populating body if field is not a nested
                # schema OR has no value OR method supported
                if nested_schema is None or not v or method not in nested_schema.get('methods', []):
                    continue

                # TODO: does this cover all edit to a model, e.g., appends, dict update, etc?
                #       could a root validator do this better?
                # only add nested value to body if they have been modified
                if nested is not None and isinstance(v, list):
                    _v = []
                    for index, item in enumerate(getattr(getattr(self.model, nested), k)):
                        if hasattr(item, 'privates'):
                            # always include all values on create (POST) or if item is new (!id)
                            if method == 'POST' or item.id is None:
                                _v.append(v[index])
                            elif method == 'PUT' and item.modified > 0:
                                _v.append(v[index])
                        else:
                            _v.append(v[index])
                    v = _v

                if isinstance(v, (list, dict)):

                    for ref in self._schema_refs(nested_schema):
                        # ref -> the nested property type (e.g., ArtifactsModel)
                        # nested_properties -> the properties/schema for the ref type
                        nested_properties = self._schema_properties(schema, ref)

                        # update body
                        nested_body = {
                            k: self._generate_body_filtered(schema, method, nested_properties, v, k)
                        }
                        # print('nested_body', nested_body)

                        # filter out field where value doesn't exist
                        nested_body = {k: v for k, v in nested_body.items() if v}

                        # only add nested body if it has data
                        if nested_body:
                            _filtered_body.update(nested_body)
                else:
                    _filtered_body.update({k: v})
            # print('filtered body', _filtered_body)
            return _filtered_body

        if isinstance(body, list):
            return [self._generate_body_filtered(schema, method, properties, i) for i in body]

        # print('body', body)
        return body

    def _iterate_over_sublist(self, sublist_type: object) -> 'V3Type':
        """Iterate over any nested collections."""
        sublist = sublist_type(session=self._session)
        sublist.tql.add_filter(**self._base_filter)
        yield from sublist

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
        # If no id is present in the obj then returns immediately.
        if not self.model.id:  # pragma: no cover
            self.log.warning(f'A {self._type} object without an ID cannot be deleted.')
            return None

        url = f'{self._api_endpoint}/{self.model.id}'
        try:
            self.request = self._session.delete(url)
            self.log.debug(
                f'Method: ({self.request.request.method.upper()}), '
                f'Status Code: {self.request.status_code}, '
                f'URl: ({self.request.url})'
            )
        except (ConnectionError, ProxyError):  # pragma: no cover
            registry.handle_error(
                code=951,
                message_values=[
                    'OPTIONS',
                    407,
                    '{\"message\": \"Connection Error\"}',
                    self._api_endpoint,
                ],
            )
        if len(self.request.content) < 5000:
            self.log.debug(f'response text: {self.request.text}')
        else:  # pragma: no cover
            self.log.debug('response text: (text to large to log)')

        if not self.success(self.request):
            err = self.request.text or self.request.reason
            if self.request.status_code == 404:
                registry.handle_error(
                    code=952,
                    message_values=[
                        self.request.request.method.upper(),
                        self.request.status_code,
                        err,
                        self.request.url,
                    ],
                )
            registry.handle_error(
                code=200,
                message_values=[self.request.status_code, err, self.request.url],
            )
        return self.request

    @cached_property
    def fields(self) -> dict:
        """Return the field data for this object."""
        _fields = {}
        r = self._session.options(f'{self._api_endpoint}/fields', params={})
        if r.ok:
            _fields = r.json().get('data', {})
        return _fields

    def get(
        self,
        all_available_fields: Optional[bool] = False,
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
            all_available_fields: If True all available fields will be returned.
            object_id: The unique id of the object to be returned.
            params: Dict of the params to be sent while retrieving the Artifacts objects.
        """
        object_id = object_id or self.model.id
        params = params or {}
        url = f'{self._api_endpoint}/{object_id}'

        # convert all keys to camel case
        params = {self._utils.snake_to_camel(k): v for k, v in params.items()}

        # special parameter for indicators to enable the return the the indicator fields
        # (value1, value2, value3) on std-custom/custom-custom indicator types.
        if self.type_ == 'Indicator':
            params.setdefault('fields', []).append('genericCustomIndicatorValues')

        # add fields parameter if provided
        if all_available_fields is True:
            params['fields'] = list(self.available_fields)

        if not object_id:  # pragma: no cover
            message = '{"message": "No ID provided.", "status": "Error"}'
            registry.handle_error(code=952, message_values=['GET', '404', message, url])

        try:
            self.request = self._session.get(
                url, params=params, headers={'content-type': 'application/json'}
            )
            self.log.debug(
                f'Method: ({self.request.request.method.upper()}), '
                f'Status Code: {self.request.status_code}, '
                f'URl: ({self.request.url})'
            )
        except (ConnectionError, ProxyError):  # pragma: no cover
            registry.handle_error(
                code=951,
                message_values=[
                    'OPTIONS',
                    407,
                    '{\"message\": \"Connection Error\"}',
                    self._api_endpoint,
                ],
            )

        # log content for debugging
        response_text = 'response text: (text to large to log)'
        if len(self.request.content) < 5000:
            response_text = self.request.text
        self.log.debug(f'response text: {response_text}')

        if not self.success(self.request):
            err = self.request.text or self.request.reason
            if self.request.status_code == 404:
                registry.handle_error(
                    code=952,
                    message_values=['GET', self.request.status_code, err, self.request.url],
                )
            registry.handle_error(
                code=951,
                message_values=['GET', self.request.status_code, err, self.request.url],
            )
        self.model = self.request.json().get('data')

        return self.request

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

    @property
    def post_properties(self) -> List[str]:
        """Return all the properties available in POST requests."""
        post_properties = []
        for p, pd in sorted(self.properties.items()):
            read_only = pd.get('read-only', False)
            if not read_only:
                post_properties.append(p)

        return post_properties

    @cached_property
    def properties(self) -> dict:
        """Return defined API properties for the current object."""
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
            registry.handle_error(
                code=951,
                message_values=[
                    'OPTIONS',
                    407,
                    '{\"message\": \"Connection Error\"}',
                    self._api_endpoint,
                ],
            )
        return _properties

    @property
    def put_properties(self) -> List[str]:
        """Return all the properties available in PUT requests."""
        put_properties = []
        for p, pd in sorted(self.properties.items()):
            # get read-only value for display and required value
            updatable = pd.get('updatable', True)
            read_only = pd.get('read-only', False)
            if not read_only:
                if updatable:
                    put_properties.append(p)

        return put_properties

    @property
    def required_properties(self) -> List[str]:
        """Return a list of required fields for current object."""
        rp = []
        for p, pd in self.properties.items():
            if pd.get('required'):
                rp.append(p)
        return rp

    # TODO: [low] WIP
    # @property
    # def results(self):
    #     """Return blah"""

    #     # local scope
    #     model = self.model
    #     request = self.request
    #     post_properties = self.post_properties
    #     properties = self.properties
    #     put_properties = self.put_properties

    #     class Results:
    #         @property
    #         def writable(self):
    #             """Return writable fields."""
    #             _includes = {}
    #             for field in post_properties:
    #                 property = properties.get(field)
    #                 if (
    #                     property.get('appliesTo')
    #                     and model.type not in property.get('appliesTo')
    #                     or property.get('readOnly') is True
    #                 ):
    #                     continue
    #                 _includes[field] = ...
    #             # return model.dict(include=_includes)
    #             return model.json(include=_includes, indent=4)

    #         @property
    #         def raw(self):
    #             return request.json()

    #     return Results()

    def submit(self) -> Response:
        """Create or Update the Case Management object.

        This is determined based on if the id is already present in the object.
        """
        method = 'POST'
        url = self._api_endpoint
        if self.model.id:
            url = f'{url}/{self.model.id}'
            method = 'PUT'
        body = self._generate_body(method)

        # make the request
        self.request = self._session.request(
            method, url, json=body, headers={'content-type': 'application/json'}
        )

        # log content for debugging
        self.log.debug(f'action=submit, method={method}, url={url}, body={body}')
        self.log.debug(
            f'action=submit-response, method={self.request.request.method}, '
            f'url={self.request.request.url}'
        )
        response_text = 'response text: (text to large to log)'
        if len(self.request.content) < 5000:
            response_text = self.request.text
        self.log.debug(f'action=submit, response-text={response_text}')

        if not self.success(self.request):  # pragma: no cover
            err = self.request.text or self.request.reason
            if self.request.status_code == 404:
                registry.handle_error(
                    code=952,
                    message_values=[
                        self.request.request.method.upper(),
                        self.request.status_code,
                        err,
                        self.request.url,
                    ],
                )
            registry.handle_error(
                code=951,
                message_values=[
                    self.request.request.method,
                    self.request.status_code,
                    err,
                    self.request.url,
                ],
            )

        r_json = self.request.json().get('data', self.request.json())

        # TODO: [high] Unsure if the entire model should be reset or just the id.
        #       If entire model the inner objects get ids set which is nice.
        new_id = r_json.get('data', r_json).get('id')
        if not new_id:
            return self.request

        self.model.id = new_id
        return self.request

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

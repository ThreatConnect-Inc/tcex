"""Case Management Abstract Base Class"""
# standard library
import logging
from abc import ABC
from typing import Any, Dict, TYPE_CHECKING, List, Optional, Union

# third-party
from requests import Response
from requests.exceptions import ProxyError

# first-party
from tcex.backports import cached_property
from tcex.pleb import Event
from tcex.utils import Utils

if TYPE_CHECKING:
    # first-party
    from tcex.case_management.artifact import Artifact
    from tcex.case_management.case import Case
    from tcex.case_management.note import Note
    from tcex.case_management.tag import Tag
    from tcex.case_management.task import Task
    from tcex.case_management.workflow_event import WorkflowEvent

    # Case Management Types
    CaseManagementType = Union[
        Artifact,
        Case,
        Note,
        Tag,
        Task,
        WorkflowEvent,
    ]

# get tcex logger
logger = logging.getLogger('tcex')


class CaseManagementABC(ABC):
    """Case Management Abstract Base Class

    This class is a base class for Case Management classes that use
    multi-inheritance with a pydantic BaseModel class. To ensure
    properties are not added to the model both @property and @setter
    methods are used.
    """

    def __init__(self, session) -> None:
        """Initialize class properties."""
        self._session = session

        # properties
        self._event = Event()
        self._utils = Utils()
        self.log = logger

    @property
    def _api_endpoint(self) -> dict:  # pragma: no cover
        """Return the type specific API endpoint."""
        raise NotImplementedError('Child class must implement this property.')

    @property
    def _base_filter(self) -> dict:  # pragma: no cover
        """Return the object as an entity."""
        raise NotImplementedError('Child class must implement this property.')

    def _schema_properties(self, schema: dict, ref: str) -> dict:
        """Return the schema properties for the ref."""
        properties = schema.get('definitions', {}).get(ref, {}).get('properties', {})

        return properties

    def _schema_refs(self, attribute_property: dict) -> list[str]:
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

    # TODO: [low] does this output a dict or json string?
    def _generate_body(self, method: str) -> dict:
        """Return the generated POST body."""
        schema = self.model.schema(ref_template='{model}')
        properties = self._schema_properties(schema, schema.get('$ref'))
        raw_body = self.model.dict(by_alias=True, exclude_none=True)
        return self._generate_body_filtered(schema, method, properties, raw_body)

    def _generate_body_filtered(
        self, schema: dict, method: str, properties: dict, body: Any
    ) -> dict:
        """Return body with null, read-only, and not updatable fields removed."""
        if isinstance(body, dict):
            safe_data = body.copy()  # make a copy of the original
            _filtered_body = {}
            for k, v in safe_data.items():
                nested_schema = properties.get(k)

                # skip populating body if field has no value, is read-only, or not updatable
                if nested_schema is None or not v or method not in nested_schema.get('methods', []):
                    continue

                if isinstance(v, (list, dict)):
                    for ref in self._schema_refs(nested_schema):
                        nested_properties = self._schema_properties(schema, ref)

                        # update body
                        nested_body = {
                            k: self._generate_body_filtered(schema, method, nested_properties, v)
                        }

                        # filter out field where value doesn't exist
                        nested_body = {k: v for k, v in nested_body.items() if v}
                        _filtered_body.update(nested_body)
                else:
                    _filtered_body.update({k: v})
            return _filtered_body
        elif isinstance(body, list):
            return [self._generate_body_filtered(schema, method, properties, i) for i in body]

        return body

    def _iterate_over_sublist(self, sublist_type: object) -> 'CaseManagementType':
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
            self.log.warning('A case without an ID cannot be deleted.')
            return

        url = f'{self._api_endpoint}/{self.model.id}'
        r = None
        try:
            r = self._session.delete(url)
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
        if len(r.content) < 5000:
            self.log.debug(f'response text: {r.text}')
        else:  # pragma: no cover
            self.log.debug('response text: (text to large to log)')
        if not self.success(r):
            err = r.text or r.reason
            if r.status_code == 404:
                self._event.send(
                    'handle_error',
                    code=952,
                    message_values=[r.request.method.upper(), r.status_code, err, r.url],
                )
            self._event.send('handle_error', code=200, message_values=[r.status_code, err, r.url])
        return

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
        params = params or {}

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
            r = self._session.get(url, params=params, headers={'content-type': 'application/json'})
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
        self.log.debug(
            f'Method: ({r.request.method.upper()}), '
            f'Status Code: {r.status_code}, '
            f'URl: ({r.url})'
        )
        if len(r.content) < 5000:
            self.log.debug(f'response text: {r.text}')
        else:  # pragma: no cover
            self.log.debug('response text: (text to large to log)')
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

        return r

    @property
    def model(self) -> 'CaseManagementType':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['CaseManagementType', dict]) -> None:
        """Create model using the provided data."""
        if isinstance(data, type(self._model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is already a model, nothing required to change
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
        r = self._session.request(
            method, url, json=body, headers={'content-type': 'application/json'}
        )

        self.log.debug(f'body: {body}')
        if len(r.content) < 5000:
            self.log.debug(f'response text: {r.text}')
        else:  # pragma: no cover
            self.log.debug('response text: (text to large to log)')

        if not self.success(r):  # pragma: no cover
            err = r.text or r.reason
            if r.status_code == 404:
                self._event.send(
                    'handle_error',
                    code=952,
                    message_values=[r.request.method.upper(), r.status_code, err, r.url],
                )
            self._event.send(
                'handle_error',
                code=951,
                message_values=[r.request.method, r.status_code, err, r.url],
            )

        r_json = r.json().get('data', r.json())

        # TODO: [high] Unsure if the entire model should be reset or just the id.
        #       If entire model the inner objects get ids set which is nice.
        new_id = r_json.get('data', r_json).get('id')
        if not new_id:
            return r
        self.model.id = new_id
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

"""TcEx Framework Module"""

# standard library
import json
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_filter import SecurityLabelFilter
from tcex.api.tc.v3.security_labels.security_label_model import (
    SecurityLabelModel,
    SecurityLabelsModel,
)


class SecurityLabel(ObjectABC):
    """SecurityLabels Object.

    Args:
        color (str, kwargs): Color of the security label.
        description (str, kwargs): Description of the security label.
        name (str, kwargs): Name of the security label.
        owner (str, kwargs): The name of the Owner of the Label.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: SecurityLabelModel = SecurityLabelModel(**kwargs)
        self._nested_field_name = 'securityLabels'
        self._nested_filter = 'has_security_label'
        self.type_ = 'Security Label'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.SECURITY_LABELS.value

    @property
    def model(self) -> SecurityLabelModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | SecurityLabelModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    def remove(self, params: dict | None = None):
        """Remove a nested object."""
        method = 'PUT'
        unique_id = self._calculate_unique_id()

        # validate an id is available
        self._validate_id(unique_id.get('value'), '')

        body = json.dumps(
            {
                self._nested_field_name: {
                    'data': [{unique_id.get('filter'): unique_id.get('value')}],
                    'mode': 'delete',
                }
            }
        )

        # get the unique id value for id, xid, summary, etc ...
        parent_api_endpoint = self._parent_data.get('api_endpoint')
        parent_unique_id = self._parent_data.get('unique_id')
        url = f'{parent_api_endpoint}/{parent_unique_id}'

        # validate parent an id is available
        self._validate_id(parent_unique_id, url)

        self._request(
            method=method,
            url=url,
            body=body,
            headers={'content-type': 'application/json'},
            params=params,
        )

        return self.request


class SecurityLabels(ObjectCollectionABC):
    """SecurityLabels Collection.

    # Example of params input
    {
        'result_limit': 100,  # Limit the retrieved results.
        'result_start': 10,  # Starting count used for pagination.
        'fields': ['caseId', 'summary']  # Select additional return fields.
    }

    Args:
        session (Session): Session object configured with TC API Auth.
        tql_filters (list): List of TQL filters.
        params (dict): Additional query params (see example above).
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = SecurityLabelsModel(**kwargs)
        self.type_ = 'security_labels'

    def __iter__(self) -> Iterator[SecurityLabel]:
        """Return CM objects."""
        return self.iterate(base_class=SecurityLabel)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.SECURITY_LABELS.value

    @property
    def filter(self) -> SecurityLabelFilter:
        """Return the type specific filter object."""
        return SecurityLabelFilter(self.tql)

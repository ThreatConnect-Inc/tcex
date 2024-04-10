"""TcEx Framework Module"""
# standard library
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelModel
from tcex.api.tc.v3.victim_attributes.victim_attribute_filter import VictimAttributeFilter
from tcex.api.tc.v3.victim_attributes.victim_attribute_model import (
    VictimAttributeModel,
    VictimAttributesModel,
)

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel  # CIRCULAR-IMPORT


class VictimAttribute(ObjectABC):
    """VictimAttributes Object.

    Args:
        default (bool, kwargs): A flag indicating that this is the default attribute of its type
            within the object. Only applies to certain attribute and data types.
        pinned (bool, kwargs): A flag indicating that the attribute has been noted for importance.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified).
        source (str, kwargs): The attribute source.
        type (str, kwargs): The attribute type.
        value (str, kwargs): The attribute value.
        victim_id (int, kwargs): Victim associated with attribute.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: VictimAttributeModel = VictimAttributeModel(**kwargs)
        self._nested_field_name = 'victimAttributes'
        self._nested_filter = 'has_victim_attribute'
        self.type_ = 'Victim Attribute'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ATTRIBUTES.value

    @property
    def model(self) -> VictimAttributeModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | VictimAttributeModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    @property
    def security_labels(self) -> Generator['SecurityLabel', None, None]:
        """Yield SecurityLabel from SecurityLabels."""
        # first-party
        from tcex.api.tc.v3.security_labels.security_label import SecurityLabels

        yield from self._iterate_over_sublist(SecurityLabels)  # type: ignore

    def stage_security_label(self, data: dict | ObjectABC | SecurityLabelModel):
        """Stage security_label on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = SecurityLabelModel(**data)

        if not isinstance(data, SecurityLabelModel):
            raise RuntimeError('Invalid type passed in to stage_security_label')
        data._staged = True
        self.model.security_labels.data.append(data)  # type: ignore


class VictimAttributes(ObjectCollectionABC):
    """VictimAttributes Collection.

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
        self._model = VictimAttributesModel(**kwargs)
        self.type_ = 'victim_attributes'

    def __iter__(self) -> Iterator[VictimAttribute]:
        """Return CM objects."""
        return self.iterate(base_class=VictimAttribute)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ATTRIBUTES.value

    @property
    def filter(self) -> VictimAttributeFilter:
        """Return the type specific filter object."""
        return VictimAttributeFilter(self.tql)

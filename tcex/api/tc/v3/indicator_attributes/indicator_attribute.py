"""IndicatorAttribute / IndicatorAttributes Object"""
# standard library
from typing import TYPE_CHECKING, Iterator, Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.indicator_attributes.indicator_attribute_filter import IndicatorAttributeFilter
from tcex.api.tc.v3.indicator_attributes.indicator_attribute_model import (
    IndicatorAttributeModel,
    IndicatorAttributesModel,
)
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel


class IndicatorAttributes(ObjectCollectionABC):
    """IndicatorAttributes Collection.

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
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = IndicatorAttributesModel(**kwargs)
        self.type_ = 'indicator_attributes'

    def __iter__(self) -> 'IndicatorAttribute':
        """Iterate over CM objects."""
        return self.iterate(base_class=IndicatorAttribute)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATOR_ATTRIBUTES.value

    @property
    def filter(self) -> 'IndicatorAttributeFilter':
        """Return the type specific filter object."""
        return IndicatorAttributeFilter(self.tql)


class IndicatorAttribute(ObjectABC):
    """IndicatorAttributes Object.

    Args:
        default (bool, kwargs): A flag indicating that this is the default attribute of its type
            within the object. Only applies to certain attribute and data types.
        indicator_id (int, kwargs): Indicator associated with attribute.
        pinned (bool, kwargs): A flag indicating that the attribute has been noted for importance.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified).
        source (str, kwargs): The attribute source.
        type (str, kwargs): The attribute type.
        value (str, kwargs): The attribute value.
    """

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = IndicatorAttributeModel(**kwargs)
        self._nested_field_name = 'attributes'
        self._nested_filter = 'has_indicator_attribute'
        self.type_ = 'Indicator Attribute'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATOR_ATTRIBUTES.value

    @property
    def model(self) -> 'IndicatorAttributeModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['IndicatorAttributeModel', dict]):
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
    def security_labels(self) -> Iterator['SecurityLabel']:
        """Yield SecurityLabel from SecurityLabels."""
        # first-party
        from tcex.api.tc.v3.security_labels.security_label import SecurityLabels

        yield from self._iterate_over_sublist(SecurityLabels)

    def stage_security_label(self, data: Union[dict, 'ObjectABC', 'SecurityLabelModel']):
        """Stage security_label on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = SecurityLabelModel(**data)

        if not isinstance(data, SecurityLabelModel):
            raise RuntimeError('Invalid type passed in to stage_security_label')
        data._staged = True
        self.model.security_labels.data.append(data)

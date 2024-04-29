"""TcEx Framework Module"""

# standard library
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_attributes.case_attribute_filter import CaseAttributeFilter
from tcex.api.tc.v3.case_attributes.case_attribute_model import (
    CaseAttributeModel,
    CaseAttributesModel,
)
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel  # CIRCULAR-IMPORT


class CaseAttribute(ObjectABC):
    """CaseAttributes Object.

    Args:
        case_id (int, kwargs): Case associated with attribute.
        default (bool, kwargs): A flag indicating that this is the default attribute of its type
            within the object. Only applies to certain attribute and data types.
        pinned (bool, kwargs): A flag indicating that the attribute has been noted for importance.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified).
        source (str, kwargs): The attribute source.
        type (str, kwargs): The attribute type.
        value (str, kwargs): The attribute value.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: CaseAttributeModel = CaseAttributeModel(**kwargs)
        self._nested_field_name = 'attributes'
        self._nested_filter = 'has_case_attribute'
        self.type_ = 'Case Attribute'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CASE_ATTRIBUTES.value

    @property
    def model(self) -> CaseAttributeModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | CaseAttributeModel):
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


class CaseAttributes(ObjectCollectionABC):
    """CaseAttributes Collection.

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
        self._model = CaseAttributesModel(**kwargs)
        self.type_ = 'case_attributes'

    def __iter__(self) -> Iterator[CaseAttribute]:
        """Return CM objects."""
        return self.iterate(base_class=CaseAttribute)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CASE_ATTRIBUTES.value

    @property
    def filter(self) -> CaseAttributeFilter:
        """Return the type specific filter object."""
        return CaseAttributeFilter(self.tql)

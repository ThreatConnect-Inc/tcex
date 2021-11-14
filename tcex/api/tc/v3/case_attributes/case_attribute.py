"""CaseAttribute / CaseAttributes Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_attributes.case_attribute_filter import CaseAttributeFilter
from tcex.api.tc.v3.case_attributes.case_attribute_model import (
    CaseAttributeModel,
    CaseAttributesModel,
)
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


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

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = CaseAttributesModel(**kwargs)
        self.type_ = 'case_attributes'

    def __iter__(self) -> 'CaseAttribute':
        """Iterate over CM objects."""
        return self.iterate(base_class=CaseAttribute)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CASE_ATTRIBUTES.value

    @property
    def filter(self) -> 'CaseAttributeFilter':
        """Return the type specific filter object."""
        return CaseAttributeFilter(self.tql)


class CaseAttribute(ObjectABC):
    """CaseAttributes Object.

    Args:
        case_id (int, kwargs): Case associated with attribute.
        default (bool, kwargs): A flag indicating that this is the default attribute of its type
            within the object. Only applies to certain attribute and data types.
        source (str, kwargs): The attribute source.
        type (str, kwargs): The attribute type.
        value (str, kwargs): Attribute value.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = CaseAttributeModel(**kwargs)
        self._nested_filter = 'has_case_attribute'
        self.type_ = 'Case Attribute'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CASE_ATTRIBUTES.value

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_
        if hasattr(self.model, 'type'):
            type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}

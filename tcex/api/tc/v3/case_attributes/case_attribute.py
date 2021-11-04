"""CaseAttribute / CaseAttributes Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_attributes.case_attribute_filter import CaseAttributeFilter
from tcex.api.tc.v3.case_attributes.case_attribute_model import CaseAttributeModel, CaseAttributesModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tql.tql_operator import TqlOperator


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
        self._type = 'case_attributes'

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


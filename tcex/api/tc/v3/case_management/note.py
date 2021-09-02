"""ThreatConnect Note"""
# third-party
from pydantic import BaseModel

# first-party
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_note import FilterNote  # pylint: disable=cyclic-import
from tcex.api.tc.v3.case_management.models.note_model import NoteData, NoteModel, NotesModel
from tcex.api.tc.v3.case_management.tql import TQL


class Notes(CaseManagementCollectionABC):
    """ThreatConnect Notes Object

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
        initial_response: Initial data from ThreatConnect API.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the objects.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = NotesModel(**kwargs)

    def __iter__(self) -> 'Note':
        """Object iterator"""
        return self.iterate(base_class=Note)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.NOTES.value

    @property
    def filter(self) -> FilterNote:
        """Return instance of FilterNotes Object."""
        return FilterNote(self._session, self.tql)


class Note(CaseManagementABC):
    """Note object for Case Management."""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        super().__init__(kwargs.pop('session'))
        self._model = NoteModel(**kwargs)

    def _base_filter(self) -> dict:
        return {
            'keyword': 'noteId',
            'operator': TQL.Operator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.NOTES.value

    @property
    def as_entity(self):
        """Return the entity representation of the Note."""
        return {'type': 'Note', 'value': self.model.summary, 'id': self.model.id}

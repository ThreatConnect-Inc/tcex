"""Case Management Artifact"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_artifact import FilterArtifact
from tcex.api.tc.v3.case_management.models.artifact_model import ArtifactModel, ArtifactsModel
from tcex.api.tc.v3.case_management.models.note_model import NoteModel
from tcex.api.tc.v3.case_management.tql import TQL


class Artifacts(CaseManagementCollectionABC):
    """Artifact collections object

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
        session: List of TQL filters.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the objects.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = ArtifactsModel(**kwargs)

    def __iter__(self) -> 'Artifact':
        """Iterate over CM objects."""
        return self.iterate(base_class=Artifact)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACTS.value

    @property
    def filter(self) -> 'FilterArtifact':
        """Return the type specific filter object."""
        return FilterArtifact(self._session, self.tql)


class Artifact(CaseManagementABC):
    """Case Management Artifact"""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        # TODO: [high] @bpurdy - Might need to save id for submit request.
        #       Might be able to do a try catch though in parent.
        super().__init__(kwargs.pop('session', None))
        self._model = ArtifactModel(**kwargs)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACTS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'artifactid',
            'operator': TQL.Operator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def notes(self):
        """Return a notes collection."""
        # first-party
        from tcex.api.tc.v3.case_management.note import Notes

        yield from self._iterate_over_sublist(Notes)

    # TODO: [high] @bpurdy - is the doc string here correct? not everything is listed, but
    #       not everything is applicable, correct?
    def add_note(self, **kwargs) -> None:
        """Add a Note to object.

        Args:
            text (str, kwargs): The **text** for the Note.
        """
        self.model.notes.data.append(NoteModel(**kwargs))

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""

        return {'type': 'Artifact', 'id': self.model.id, 'value': self.model.summary}

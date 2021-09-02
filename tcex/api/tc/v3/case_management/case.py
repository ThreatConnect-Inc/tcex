"""ThreatConnect Case"""
# first-party
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_case import FilterCase
from tcex.api.tc.v3.case_management.models.artifact_model import ArtifactModel, ArtifactsModel
from tcex.api.tc.v3.case_management.models.case_model import CaseData, CaseModel
from tcex.api.tc.v3.case_management.models.note_model import NoteModel, NotesModel
from tcex.api.tc.v3.case_management.models.tag_model import TagModel, TagsModel
from tcex.api.tc.v3.case_management.models.task_model import TaskModel, TasksModel
from tcex.api.tc.v3.case_management.tql import TQL


class Cases(CaseManagementCollectionABC):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = CaseData(**kwargs)

    def __iter__(self) -> 'Case':
        """Object iterator"""
        return self.iterate(base_class=Case)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.CASES.value

    @property
    def filter(self) -> 'FilterCase':
        """Return instance of FilterCases Object."""
        return FilterCase(self._session, self.tql)


class Case(CaseManagementABC):
    """Case object for Case Management."""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        # Might need to save id for submit request. Might be able to do a try catch though in parent.
        super().__init__(kwargs.pop('session', None))
        self._model = CaseModel(**kwargs)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.CASES.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'caseid',
            'operator': TQL.Operator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def artifacts(self):
        # first-party
        from tcex.api.tc.v3.case_management.artifact import Artifacts

        yield from self._iterate_over_sublist(Artifacts)

    @property
    def notes(self):
        # first-party
        from tcex.api.tc.v3.case_management.note import Notes

        yield from self._iterate_over_sublist(Notes)

    @property
    def tags(self):
        # first-party
        from tcex.api.tc.v3.case_management.tag import Tags

        yield from self._iterate_over_sublist(Tags)

    def add_artifact(self, **kwargs) -> None:
        """Add a Artifact to a Case."""
        self.model.artifacts.data.append(ArtifactModel(**kwargs))

    def add_note(self, **kwargs) -> None:
        """Add a Note to a Case."""
        self.model.notes.data.append(NoteModel(**kwargs))

    def add_tag(self, **kwargs) -> None:
        """Add a Tag to a Case."""
        self.model.tags.data.append(TagModel(**kwargs))

    def add_task(self, **kwargs) -> None:
        """Add a Task to a Case."""
        self.model.tasks.data.append(TaskModel(**kwargs))

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the Case."""

        return {
            'type': 'Case',
            'id': self.model.id,
            'value': self.model.name,
        }

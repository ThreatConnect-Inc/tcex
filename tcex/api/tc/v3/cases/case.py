"""TcEx Framework Module"""

# standard library
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING, Self

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.case_attributes.case_attribute_model import CaseAttributeModel
from tcex.api.tc.v3.cases.case_filter import CaseFilter
from tcex.api.tc.v3.cases.case_model import CaseModel, CasesModel
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel
from tcex.api.tc.v3.notes.note_model import NoteModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.tags.tag_model import TagModel
from tcex.api.tc.v3.tasks.task_model import TaskModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.case_attributes.case_attribute import CaseAttribute  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.groups.group import Group  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.indicators.indicator import Indicator  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.notes.note import Note  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.tags.tag import Tag  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.tasks.task import Task  # CIRCULAR-IMPORT


class Case(ObjectABC):
    """Cases Object.

    Args:
        artifacts (Artifacts, kwargs): A list of Artifacts corresponding to the Case.
        assignee (Assignee, kwargs): The user or group Assignee object for the Case.
        associated_cases (Cases, kwargs): A list of Cases associated with this Case.
        associated_groups (Groups, kwargs): A list of Groups associated with this Case.
        associated_indicators (Indicators, kwargs): A list of Indicators associated with this Case.
        attributes (CaseAttributes, kwargs): A list of Attributes corresponding to the Case.
        case_close_time (str, kwargs): The date and time that the Case was closed.
        case_detection_time (str, kwargs): The date and time that ends the user initiated Case
            duration.
        case_occurrence_time (str, kwargs): The date and time that starts the user initiated Case
            duration.
        case_open_time (str, kwargs): The date and time that the Case was first opened.
        description (str, kwargs): The description of the Case.
        name (str, kwargs): The name of the Case.
        notes (Notes, kwargs): A list of Notes corresponding to the Case.
        resolution (str, kwargs): The Case resolution.
        severity (str, kwargs): The Case severity.
        status (str, kwargs): The Case status.
        tags (Tags, kwargs): A list of Tags corresponding to the Case (NOTE: Setting this parameter
            will replace any existing tag(s) with the one(s) specified).
        tasks (Tasks, kwargs): A list of Tasks corresponding to the Case.
        user_access (Users, kwargs): A list of Users that, when defined, are the only ones allowed
            to view or edit the Case.
        workflow_events (WorkflowEvents, kwargs): A list of workflowEvents (timeline) corresponding
            to the Case.
        workflow_template (WorkflowTemplate, kwargs): The Template that the Case is populated by.
        xid (str, kwargs): The **xid** for the Case.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: CaseModel = CaseModel(**kwargs)
        self._nested_field_name = 'cases'
        self._nested_filter = 'has_case'
        self.type_ = 'Case'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CASES.value

    @property
    def model(self) -> CaseModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | CaseModel):
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
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_

        return {'type': type_, 'id': self.model.id, 'value': self.model.name}

    @property
    def artifacts(self) -> Generator['Artifact', None, None]:
        """Yield Artifact from Artifacts."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact import Artifacts

        yield from self._iterate_over_sublist(Artifacts)  # type: ignore

    @property
    def associated_cases(self) -> Generator[Self, None, None]:
        """Yield Case from Cases."""
        # Ensure the current item is not returned as a association
        for case in self._iterate_over_sublist(Cases):  # type: ignore
            if case.model.id == self.model.id:
                continue
            yield case  # type: ignore

    @property
    def associated_groups(self) -> Generator['Group', None, None]:
        """Yield Group from Groups."""
        # first-party
        from tcex.api.tc.v3.groups.group import Groups

        yield from self._iterate_over_sublist(Groups)  # type: ignore

    @property
    def associated_indicators(self) -> Generator['Indicator', None, None]:
        """Yield Indicator from Indicators."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator import Indicators

        yield from self._iterate_over_sublist(Indicators)  # type: ignore

    @property
    def attributes(self) -> Generator['CaseAttribute', None, None]:
        """Yield Attribute from Attributes."""
        # first-party
        from tcex.api.tc.v3.case_attributes.case_attribute import CaseAttributes

        yield from self._iterate_over_sublist(CaseAttributes)  # type: ignore

    @property
    def notes(self) -> Generator['Note', None, None]:
        """Yield Note from Notes."""
        # first-party
        from tcex.api.tc.v3.notes.note import Notes

        yield from self._iterate_over_sublist(Notes)  # type: ignore

    @property
    def tags(self) -> Generator['Tag', None, None]:
        """Yield Tag from Tags."""
        # first-party
        from tcex.api.tc.v3.tags.tag import Tags

        yield from self._iterate_over_sublist(Tags)  # type: ignore

    @property
    def tasks(self) -> Generator['Task', None, None]:
        """Yield Task from Tasks."""
        # first-party
        from tcex.api.tc.v3.tasks.task import Tasks

        yield from self._iterate_over_sublist(Tasks)  # type: ignore

    def stage_artifact(self, data: dict | ObjectABC | ArtifactModel):
        """Stage artifact on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = ArtifactModel(**data)

        if not isinstance(data, ArtifactModel):
            raise RuntimeError('Invalid type passed in to stage_artifact')
        data._staged = True
        self.model.artifacts.data.append(data)  # type: ignore

    # pylint: disable=redefined-builtin
    def stage_assignee(self, type: str, data: dict | ObjectABC | UserModel | UserGroupModel):
        """Stage artifact on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif type.lower() == 'user' and isinstance(data, dict):
            data = UserModel(**data)
        elif type.lower() == 'group' and isinstance(data, dict):
            data = UserGroupModel(**data)

        if not isinstance(data, UserModel | UserGroupModel):
            raise RuntimeError('Invalid type passed in to stage_assignee')
        data._staged = True
        self.model.assignee._staged = True
        self.model.assignee.type = type
        self.model.assignee.data = data  # type: ignore

    def stage_associated_case(self, data: dict | ObjectABC | CaseModel):
        """Stage case on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = CaseModel(**data)

        if not isinstance(data, CaseModel):
            raise RuntimeError('Invalid type passed in to stage_associated_case')
        data._staged = True
        self.model.associated_cases.data.append(data)  # type: ignore

    def stage_associated_group(self, data: dict | ObjectABC | GroupModel):
        """Stage group on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = GroupModel(**data)

        if not isinstance(data, GroupModel):
            raise RuntimeError('Invalid type passed in to stage_associated_group')
        data._staged = True
        self.model.associated_groups.data.append(data)  # type: ignore

    def stage_associated_indicator(self, data: dict | ObjectABC | IndicatorModel):
        """Stage indicator on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = IndicatorModel(**data)

        if not isinstance(data, IndicatorModel):
            raise RuntimeError('Invalid type passed in to stage_associated_indicator')
        data._staged = True
        self.model.associated_indicators.data.append(data)  # type: ignore

    def stage_attribute(self, data: dict | ObjectABC | CaseAttributeModel):
        """Stage attribute on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = CaseAttributeModel(**data)

        if not isinstance(data, CaseAttributeModel):
            raise RuntimeError('Invalid type passed in to stage_attribute')
        data._staged = True
        self.model.attributes.data.append(data)  # type: ignore

    def stage_note(self, data: dict | ObjectABC | NoteModel):
        """Stage note on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = NoteModel(**data)

        if not isinstance(data, NoteModel):
            raise RuntimeError('Invalid type passed in to stage_note')
        data._staged = True
        self.model.notes.data.append(data)  # type: ignore

    def stage_tag(self, data: dict | ObjectABC | TagModel):
        """Stage tag on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = TagModel(**data)

        if not isinstance(data, TagModel):
            raise RuntimeError('Invalid type passed in to stage_tag')
        data._staged = True
        self.model.tags.data.append(data)  # type: ignore

    def stage_task(self, data: dict | ObjectABC | TaskModel):
        """Stage task on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = TaskModel(**data)

        if not isinstance(data, TaskModel):
            raise RuntimeError('Invalid type passed in to stage_task')
        data._staged = True
        self.model.tasks.data.append(data)  # type: ignore

    def stage_user_access(self, data: dict | ObjectABC | UserModel):
        """Stage user on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = UserModel(**data)

        if not isinstance(data, UserModel):
            raise RuntimeError('Invalid type passed in to stage_user_access')
        data._staged = True
        self.model.user_access.data.append(data)  # type: ignore


class Cases(ObjectCollectionABC):
    """Cases Collection.

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
        self._model = CasesModel(**kwargs)
        self.type_ = 'cases'

    def __iter__(self) -> Iterator[Case]:
        """Return CM objects."""
        return self.iterate(base_class=Case)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CASES.value

    @property
    def filter(self) -> CaseFilter:
        """Return the type specific filter object."""
        return CaseFilter(self.tql)

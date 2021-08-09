"""ThreatConnect Case"""
# standard library
from enum import Enum
from typing import TYPE_CHECKING, Optional

# first-party
from tcex.case_management.api_endpoints import ApiEndpoints
from tcex.case_management.common_case_management import CommonCaseManagement
from tcex.case_management.common_case_management_collection import CommonCaseManagementCollection
from tcex.case_management.filter import Filter
from tcex.case_management.tql import TQL

if TYPE_CHECKING:
    # first-party
    from tcex.case_management.artifact import Artifacts
    from tcex.case_management.assignee import Assignee, User, Users
    from tcex.case_management.note import Notes
    from tcex.case_management.tag import Tags
    from tcex.case_management.task import Tasks
    from tcex.case_management.workflow_event import WorkflowEvents
    from tcex.case_management.workflow_template import WorkflowTemplate


class Cases(CommonCaseManagementCollection):
    """Case Class for Case Management Collection

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
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response: Initial data in Case Object for Artifact.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the Case objects.
    """

    def __init__(
        self,
        tcex,
        initial_response: Optional[dict] = None,
        tql_filters: Optional[list] = None,
        params: Optional[dict] = None,
    ) -> None:
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.CASES,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
        )
        if initial_response:
            for item in initial_response.get('data', []):
                self.added_items.append(Case(tcex, **item))

    def __iter__(self) -> 'Case':
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity) -> 'Case':
        """Map a dict to a Artifact.

        Args:
            entity (dict): The Artifact data.

        Returns:
            CaseManagement.Case: A Case Object.
        """
        return Case(self.tcex, **entity)

    @property
    def filter(self) -> 'FilterCases':
        """Return instance of FilterCases Object."""
        return FilterCases(ApiEndpoints.CASES, self.tcex, self.tql)


class Case(CommonCaseManagement):
    """Case object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        artifacts (Artifacts, kwargs): a list of Artifacts corresponding to the Case
        assignee (Assignee, kwargs): the user or group Assignee object for the Case
        created_by (User, kwargs): [Read-Only] The **Created By** for the Case.
        date_added (str, kwargs): [Read-Only] The **Date Added** for the Case.
        description (str, kwargs): The **Description** for the Case.
        name (str, kwargs): [Required] The **Name** for the Case.
        notes (Notes, kwargs): a list of Notes corresponding to the Case
        owner (str, kwargs): The Org/Owner name for the Case.
        related (Case, kwargs): The **Related** for the Case.
        resolution (str, kwargs): The **Resolution** for the Case.
        severity (str, kwargs): [Required] The **Severity** for the Case.
        status (str, kwargs): [Required] The **Status** for the Case.
        tags (case_management.tag.Tag, kwargs): a list of Tags corresponding to the Case
            (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified)
        tasks (case_management.task.Task, kwargs): a list of Tasks corresponding to the Case
        user_access (Users, kwargs): a list of Users that, when defined, are the only
            ones allowed to view or edit the Case
        workflow_events (WorkflowEvent, kwargs): The **Events** for the Case.
        workflow_template (WorkflowTemplate, kwargs): the Template that the Case is
            populated by.
        xid (str, kwargs): The **Xid** for the Case.
    """

    def __init__(self, tcex, **kwargs) -> None:
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.CASES, kwargs)
        self.case_filter = [
            {'keyword': 'caseid', 'operator': TQL.Operator.EQ, 'value': self.id, 'type': 'integer'}
        ]

        self._artifacts = kwargs.get('artifacts', None)
        self._assignee = kwargs.get('assignee', None)
        self._created_by = kwargs.get('created_by', None)
        self._date_added = kwargs.get('date_added', None)
        self._description = kwargs.get('description', None)
        self._name = kwargs.get('name', None)
        self._notes = kwargs.get('notes', None)
        self._owner = kwargs.get('owner', None)
        self._related = kwargs.get('related', None)
        self._resolution = kwargs.get('resolution', None)
        self._severity = kwargs.get('severity', None)
        self._status = kwargs.get('status', None)
        self._tags = kwargs.get('tags', None)
        self._tasks = kwargs.get('tasks', None)
        self._user_access = kwargs.get('user_access', None)
        self._workflow_events = kwargs.get('workflow_events', None)
        self._workflow_template = kwargs.get('workflow_template', None)
        self._xid = kwargs.get('xid', None)

    def add_artifact(self, **kwargs) -> None:
        """Add a Artifact to a Case."""
        self.artifacts.add_artifact(self.tcex.cm.artifact(**kwargs))

    def add_note(self, **kwargs) -> None:
        """Add a Note to a Case."""
        self.notes.add_note(self.tcex.cm.note(**kwargs))

    def add_tag(self, **kwargs) -> None:
        """Add a Tag to a Case."""
        self.tags.add_tag(self.tcex.cm.tag(**kwargs))

    def add_task(self, **kwargs) -> None:
        """Add a Task to a Case."""
        self.tasks.add_task(self.tcex.cm.task(**kwargs))

    @property
    def artifacts(self) -> 'Artifacts':
        """Return the **Artifacts** for the Case."""
        if self._artifacts is None or isinstance(self._artifacts, dict):
            artifacts = self._artifacts or {}
            self._artifacts = self.tcex.cm.artifacts(
                initial_response=artifacts, tql_filters=self.case_filter
            )
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts: 'Artifacts') -> None:
        """Set the **Artifacts** for the Case."""
        self._artifacts = artifacts

    @property
    def assignee(self) -> 'Assignee':
        """Return the **Assignee** for the Case."""
        if isinstance(self._assignee, dict):
            return self.tcex.cm.assignee(
                type=self._assignee.get('type'), **self._assignee.get('data')
            )
        return self._assignee

    @assignee.setter
    def assignee(self, assignee: dict) -> None:
        """Set the **Assignee** for the Case."""
        if isinstance(assignee, dict):
            self._assignee = self.tcex.cm.assignee(
                type=assignee.get('type'), **assignee.get('data')
            )
        self._assignee = assignee

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the Case."""
        return {'type': 'Case', 'id': self.id, 'value': self.name}

    @property
    def created_by(self) -> 'User':
        """Return the **Created By** for the Case."""
        if self._created_by:
            return self.tcex.cm.user(**self._created_by)
        return self._created_by

    @property
    def description(self) -> str:
        """Return the **Description** for the Case."""
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        """Set the **Description** for the Case."""
        self._description = description

    @property
    def date_added(self) -> str:
        """Return the **Date Added** for the Case."""
        return self._date_added

    def entity_mapper(self, entity: dict) -> None:
        """Update current object with provided object properties.

        Args:
            entity: An entity dict used to update the Object.
        """
        new_case = Case(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def name(self) -> str:
        """Return the **Name** for the Case."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Set the **Name** for the Case."""
        self._name = name

    @property
    def notes(self) -> 'Notes':
        """Return the **Notes** for the Case."""
        if self._notes is None or isinstance(self._notes, dict):
            notes = self._notes or {}
            self._notes = self.tcex.cm.notes(initial_response=notes, tql_filters=self.case_filter)
        return self._notes

    @notes.setter
    def notes(self, notes: 'Notes') -> None:
        """Set the **Notes** for the Case."""
        self._notes = notes

    @property
    def owner(self) -> str:
        """Return the **Owner** for the Case."""
        return self._owner

    @property
    def related(self) -> 'Cases':
        """Return the **Related Cases** for the Case."""
        if self._related:
            return self.tcex.cm.cases(initial_response=self._related, tql_filters=self.case_filter)
        return self._related

    @property
    def resolution(self) -> str:
        """Return the **Resolution** for the Case."""
        return self._resolution

    @resolution.setter
    def resolution(self, resolution: str) -> None:
        """Set the **Resolution** for the Case."""
        self._resolution = resolution

    @property
    def severity(self) -> str:
        """Return the **Severity** for the Case."""
        return self._severity

    @severity.setter
    def severity(self, severity: str):
        """Set the **Severity** for the Case."""
        self._severity = severity

    @property
    def status(self) -> str:
        """Return the **Status** for the Case."""
        return self._status

    @status.setter
    def status(self, status: str):
        """Set the **Status** for the Case."""
        self._status = status

    @property
    def tags(self) -> 'Tags':
        """Return the **Tags** for the Case."""
        if self._tags is None or isinstance(self._tags, dict):
            tags = self._tags or {}
            self._tags = self.tcex.cm.tags(initial_response=tags, tql_filters=self.case_filter)
        return self._tags

    @tags.setter
    def tags(self, tags: 'Tags') -> None:
        """Set the **Tags** for the Case."""
        self._tags = tags

    @property
    def tasks(self) -> 'Tasks':
        """Return the **Tasks** for the Case."""
        if self._tasks is None or isinstance(self._tasks, dict):
            tasks = self._tasks or {}
            self._tasks = self.tcex.cm.tasks(initial_response=tasks, tql_filters=self.case_filter)
        return self._tasks

    @tasks.setter
    def tasks(self, tasks: 'Tasks') -> None:
        """Set the **Tasks** for the Case."""
        self._tasks = tasks

    @property
    def user_access(self) -> 'Users':
        """Return the **User Access** for the Case."""
        if self._user_access is None:
            self._user_access = self.tcex.cm.users(users=None)
        elif isinstance(self._user_access, dict):
            self._user_access = self.tcex.cm.users(users=self._user_access.get('data', []))
        return self._user_access

    @user_access.setter
    def user_access(self, user_access) -> 'Users':
        """Set the **User Access** for the Case."""
        self._user_access = user_access

    @property
    def workflow_events(self) -> 'WorkflowEvents':
        """Return the **Workflow Events** for the Case."""
        if self._workflow_events:
            return self.tcex.cm.workflow_events(
                initial_response=self._workflow_events, tql_filters=self.case_filter
            )
        return self._workflow_events

    @property
    def workflow_template(self) -> 'WorkflowTemplate':
        """Return the **Workflow Template** for the Case."""
        if self._workflow_template:
            return self.tcex.cm.workflow_template(**self._workflow_template)
        return self._workflow_template

    @property
    def xid(self) -> str:
        """Return the **XID** for the Case."""
        return self._xid

    @xid.setter
    def xid(self, xid: str) -> None:
        """Set the **XID** for the Case."""
        self._xid = xid


class FilterCases(Filter):
    """Filter Object for Cases"""

    def created_by(self, operator: Enum, created_by: str) -> None:
        """Filter Cases based on **createdBy** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by: The account login of the user who created the case.
        """
        self._tql.add_filter('createdBy', operator, created_by, TQL.Type.STRING)

    def created_by_id(self, operator: Enum, created_by_id) -> None:
        """Filter Cases based on **createdById** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by_id: The user ID for the creator of the case.
        """
        self._tql.add_filter('createdById', operator, created_by_id, TQL.Type.INTEGER)

    def date_added(self, operator: Enum, date_added) -> None:
        """Filter Cases based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the case was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    def description(self, operator: Enum, description) -> None:
        """Filter Cases based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the case.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    # TODO: [low] can't add typing hint return
    @property
    def has_artifact(self):
        """Return **FilterArtifacts** for further filtering."""
        from tcex.case_management.artifact import FilterArtifacts

        artifacts = FilterArtifacts(ApiEndpoints.ARTIFACTS, self._tcex, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    # TODO: [low] can't add typing hint return
    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        from tcex.case_management.note import FilterNotes

        notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    # TODO: [low] can't add typing hint return
    @property
    def has_tag(self):
        """Return **FilterTags** for further filtering."""
        from tcex.case_management.tag import FilterTags

        tags = FilterTags(ApiEndpoints.TAGS, self._tcex, TQL())
        self._tql.add_filter('hasTag', TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)
        return tags

    # TODO: [low] can't add typing hint return
    @property
    def has_task(self):
        """Return **FilterTask** for further filtering."""
        from tcex.case_management.task import FilterTasks

        tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter Cases based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the case.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Cases based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the case.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def owner(self, operator: Enum, owner: str) -> None:
        """Filter Cases based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the case.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Cases based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name for the case.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)

    def resolution(self, operator: Enum, resolution: str) -> None:
        """Filter Cases based on **resolution** keyword.

        Args:
            operator: The operator enum for the filter.
            resolution: The resolution of the case.
        """
        self._tql.add_filter('resolution', operator, resolution, TQL.Type.STRING)

    def severity(self, operator: Enum, severity: str) -> None:
        """Filter Cases based on **severity** keyword.

        Args:
            operator: The operator enum for the filter.
            severity: The severity of the case.
        """
        self._tql.add_filter('severity', operator, severity, TQL.Type.STRING)

    def status(self, operator: Enum, status: str) -> None:
        """Filter Cases based on **status** keyword.

        Args:
            operator: The operator enum for the filter.
            status: The status of the case.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def tag(self, operator: Enum, tag: str) -> None:
        """Filter Cases based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to a case.
        """
        self._tql.add_filter('tag', operator, tag, TQL.Type.STRING)

    def target_id(self, operator: Enum, target_id: int) -> None:
        """Filter Cases based on **targetId** keyword.

        Args:
            operator: The operator enum for the filter.
            target_id: The assigned user or group ID for the case.
        """
        self._tql.add_filter('targetId', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator: Enum, target_type: str) -> None:
        """Filter Cases based on **targetType** keyword.

        Args:
            operator: The operator enum for the filter.
            target_type: The target type for this case (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TQL.Type.STRING)

    def xid(self, operator: Enum, xid: str) -> None:
        """Filter Cases based on **xid** keyword.

        Args:
            operator: The operator enum for the filter.
            xid: The XID of the case.
        """
        self._tql.add_filter('xid', operator, xid, TQL.Type.STRING)

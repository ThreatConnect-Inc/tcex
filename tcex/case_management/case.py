"""ThreatConnect Case"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


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
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Case objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
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

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        """Map a dict to a Artifact.

        Args:
            entity (dict): The Artifact data.

        Returns:
            CaseManagement.Case: A Case Object.
        """
        return Case(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterCases Object."""
        return FilterCases(ApiEndpoints.CASES, self.tcex, self.tql)


class Case(CommonCaseManagement):
    """Case object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        artifacts (Artifact, kwargs): a list of Artifacts corresponding to the Case
        assignee (Assignee, kwargs): the user or group Assignee object for the Case
        case_close_time (str, kwargs): [Read-Only] The date and time that the Case was closed.
        case_close_user (User, kwargs): [Read-Only] The user that closed the Case.
        case_detection_time (str, kwargs): The date and time that ends the user initiated Case
            duration.
        case_detection_user (User, kwargs): [Read-Only] The user that stopped the clock on Case
            duration.
        case_occurrence_time (str, kwargs): The date and time that starts the user initiated Case
            duration.
        case_occurrence_user (User, kwargs): [Read-Only] The user that started the clock on Case
            duration.
        case_open_time (str, kwargs): The date and time that the Case was first opened.
        case_open_user (User, kwargs): [Read-Only] The user that opened the Case.
        created_by (User, kwargs): [Read-Only] The **Created By** for the Case.
        date_added (str, kwargs): [Read-Only] The **Date Added** for the Case.
        description (str, kwargs): The **Description** for the Case.
        name (str, kwargs): [Required] The **Name** for the Case.
        notes (Note, kwargs): a list of Notes corresponding to the Case
        owner (str, kwargs): The Org/Owner name for the Case.
        related (Case, kwargs): The **Related** for the Case.
        resolution (str, kwargs): The **Resolution** for the Case.
        severity (str, kwargs): [Required] The **Severity** for the Case.
        status (str, kwargs): [Required] The **Status** for the Case.
        tags (case_management.tag.Tag, kwargs): a list of Tags corresponding to the Case
            (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified)
        tasks (case_management.task.Task, kwargs): a list of Tasks corresponding to the Case
        user_access (User, kwargs): a list of Users that, when defined, are the only
            ones allowed to view or edit the Case
        workflow_events (WorkflowEvent, kwargs): The **Events** for the Case.
        workflow_template (WorkflowTemplate, kwargs): the Template that the Case is
            populated by.
        xid (str, kwargs): The **Xid** for the Case.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.CASES, kwargs)
        self.case_filter = [
            {'keyword': 'caseid', 'operator': TQL.Operator.EQ, 'value': self.id, 'type': 'integer'}
        ]

        self._attributes = kwargs.get('attributes', None)
        self._artifacts = kwargs.get('artifacts', None)
        self._assignee = kwargs.get('assignee', None)
        self._case_close_time = kwargs.get('case_close_time', None)
        self._case_close_user = kwargs.get('case_close_user', None)
        self._case_detection_time = kwargs.get('case_detection_time', None)
        self._case_detection_user = kwargs.get('case_detection_user', None)
        self._case_occurrence_time = kwargs.get('case_occurrence_time', None)
        self._case_occurrence_user = kwargs.get('case_occurrence_user', None)
        self._case_open_time = kwargs.get('case_open_time', None)
        self._case_open_user = kwargs.get('case_open_user', None)
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

    def add_attribute(self, **kwargs):
        """Add a Artifact to a Case."""
        self.attributes.add_attribute(self.tcex.cm.attribute(**kwargs))

    def add_artifact(self, **kwargs):
        """Add a Artifact to a Case."""
        self.artifacts.add_artifact(self.tcex.cm.artifact(**kwargs))

    def add_note(self, **kwargs):
        """Add a Note to a Case."""
        self.notes.add_note(self.tcex.cm.note(**kwargs))

    def add_tag(self, **kwargs):
        """Add a Tag to a Case."""
        self.tags.add_tag(self.tcex.cm.tag(**kwargs))

    def add_task(self, **kwargs):
        """Add a Task to a Case."""
        self.tasks.add_task(self.tcex.cm.task(**kwargs))

    @property
    def artifacts(self):
        """Return the **Artifacts** for the Case."""
        if self._artifacts is None or isinstance(self._artifacts, dict):
            artifacts = self._artifacts or {}
            self._artifacts = self.tcex.cm.artifacts(
                initial_response=artifacts, tql_filters=self.case_filter
            )
        return self._artifacts

    @property
    def attributes(self):
        """Return the **Artifacts** for the Case."""
        if self._attributes is None or isinstance(self._attributes, dict):
            attributes = self._attributes or {}
            self._attributes = self.tcex.cm.attributes(
                initial_response=attributes, tql_filters=self.case_filter
            )
        return self._attributes

    @artifacts.setter
    def artifacts(self, artifacts):
        """Set the **Artifacts** for the Case."""
        self._artifacts = artifacts

    @property
    def assignee(self):
        """Return the **Assignee** for the Case."""
        if isinstance(self._assignee, dict):
            return self.tcex.cm.assignee(
                type=self._assignee.get('type'), **self._assignee.get('data')
            )
        return self._assignee

    @assignee.setter
    def assignee(self, assignee):
        """Set the **Assignee** for the Case."""
        if isinstance(assignee, dict):
            self._assignee = self.tcex.cm.assignee(
                type=assignee.get('type'), **assignee.get('data')
            )
        self._assignee = assignee

    @property
    def as_entity(self):
        """Return the entity representation of the Case."""
        return {'type': 'Case', 'id': self.id, 'value': self.name}

    @property
    def case_close_time(self):
        """Return the **Case Close Time** for the Case."""
        return self._case_close_time

    @property
    def case_close_user(self):
        """Return the **Case Close User** for the Case."""
        if self._case_close_user:
            return self.tcex.cm.user(**self._case_close_user)
        return self._case_close_user

    @property
    def case_detection_time(self):
        """Return the **Case Detection Time** for the Case."""
        return self._case_detection_time

    @property
    def case_detection_user(self):
        """Return the **Case Detection User** for the Case."""
        if self._case_detection_user:
            return self.tcex.cm.user(**self._case_detection_user)
        return self._case_detection_user

    @property
    def case_occurrence_time(self):
        """Return the **Case Occurrence Time** for the Case."""
        return self._case_occurrence_time

    @property
    def case_occurrence_user(self):
        """Return the **Case Occurrence User** for the Case."""
        if self._case_occurrence_user:
            return self.tcex.cm.user(**self._case_occurrence_user)
        return self._case_occurrence_user

    @property
    def case_open_time(self):
        """Return the **Case Open Time** for the Case."""
        return self._case_open_time

    @property
    def case_open_user(self):
        """Return the **Case Open User** for the Case."""
        if self._case_open_user:
            return self.tcex.cm.user(**self._case_open_user)
        return self._case_open_user

    @property
    def created_by(self):
        """Return the **Created By** for the Case."""
        if self._created_by:
            return self.tcex.cm.user(**self._created_by)
        return self._created_by

    @property
    def description(self):
        """Return the **Description** for the Case."""
        return self._description

    @description.setter
    def description(self, description):
        """Set the **Description** for the Case."""
        self._description = description

    @case_detection_time.setter
    def case_detection_time(self, case_detection_time):
        """Set the **Description** for the Case."""
        self._case_detection_time = case_detection_time

    @case_occurrence_time.setter
    def case_occurrence_time(self, case_occurrence_time):
        """Set the **Description** for the Case."""
        self._case_detection_time = case_occurrence_time

    @property
    def date_added(self):
        """Return the **Date Added** for the Case."""
        return self._date_added

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = Case(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def name(self):
        """Return the **Name** for the Case."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the **Name** for the Case."""
        self._name = name

    @property
    def notes(self):
        """Return the **Notes** for the Case."""
        if self._notes is None or isinstance(self._notes, dict):
            notes = self._notes or {}
            self._notes = self.tcex.cm.notes(initial_response=notes, tql_filters=self.case_filter)
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the **Notes** for the Case."""
        self._notes = notes

    @property
    def owner(self):
        """Return the **Owner** for the Case."""
        return self._owner

    @property
    def related(self):
        """Return the **Related Cases** for the Case."""
        if self._related:
            return self.tcex.cm.cases(initial_response=self._related, tql_filters=self.case_filter)
        return self._related

    @property
    def resolution(self):
        """Return the **Resolution** for the Case."""
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """Set the **Resolution** for the Case."""
        self._resolution = resolution

    @property
    def severity(self):
        """Return the **Severity** for the Case."""
        return self._severity

    @severity.setter
    def severity(self, severity):
        """Set the **Severity** for the Case."""
        self._severity = severity

    @property
    def status(self):
        """Return the **Status** for the Case."""
        return self._status

    @status.setter
    def status(self, status):
        """Set the **Status** for the Case."""
        self._status = status

    @property
    def tags(self):
        """Return the **Tags** for the Case."""
        if self._tags is None or isinstance(self._tags, dict):
            tags = self._tags or {}
            self._tags = self.tcex.cm.tags(initial_response=tags, tql_filters=self.case_filter)
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Set the **Tags** for the Case."""
        self._tags = tags

    @property
    def tasks(self):
        """Return the **Tasks** for the Case."""
        if self._tasks is None or isinstance(self._tasks, dict):
            tasks = self._tasks or {}
            self._tasks = self.tcex.cm.tasks(initial_response=tasks, tql_filters=self.case_filter)
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        """Set the **Tasks** for the Case."""
        self._tasks = tasks

    @property
    def user_access(self):
        """Return the **User Access** for the Case."""
        if self._user_access is None:
            self._user_access = self.tcex.cm.users(users=None)
        elif isinstance(self._user_access, dict):
            self._user_access = self.tcex.cm.users(users=self._user_access.get('data', []))
        return self._user_access

    @user_access.setter
    def user_access(self, user_access):
        """Set the **User Access** for the Case."""
        self._user_access = user_access

    @property
    def workflow_events(self):
        """Return the **Workflow Events** for the Case."""
        if self._workflow_events:
            return self.tcex.cm.workflow_events(
                initial_response=self._workflow_events, tql_filters=self.case_filter
            )
        return self._workflow_events

    @property
    def workflow_template(self):
        """Return the **Workflow Template** for the Case."""
        if self._workflow_template:
            return self.tcex.cm.workflow_template(**self._workflow_template)
        return self._workflow_template

    @property
    def xid(self):
        """Return the **XID** for the Case."""
        return self._xid

    @xid.setter
    def xid(self, xid):
        """Set the **XID** for the Case."""
        self._xid = xid


class FilterCases(Filter):
    """Filter Object for Cases"""

    def attribute(self, operator, attribute):
        """Filter Cases based on **attribute** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            attribute (str): None.
        """
        self._tql.add_filter('attribute', operator, attribute, TQL.Type.STRING)

    def case_close_time(self, operator, case_close_time):
        """Filter Cases based on **caseCloseTime** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_close_time (str): The date/time the case was closed.
        """
        self._tql.add_filter('caseCloseTime', operator, case_close_time, TQL.Type.STRING)

    def case_close_user(self, operator, case_close_user):
        """Filter Cases based on **caseCloseUser** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_close_user (str): The user who closed the case.
        """
        self._tql.add_filter('caseCloseUser', operator, case_close_user, TQL.Type.STRING)

    def case_detection_time(self, operator, case_detection_time):
        """Filter Cases based on **caseDetectionTime** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_detection_time (str): The date/time the case was detected.
        """
        self._tql.add_filter('caseDetectionTime', operator, case_detection_time, TQL.Type.STRING)

    def case_detection_user(self, operator, case_detection_user):
        """Filter Cases based on **caseDetectionUser** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_detection_user (str): The user who logged the case detection time.
        """
        self._tql.add_filter('caseDetectionUser', operator, case_detection_user, TQL.Type.STRING)

    def case_occurrence_time(self, operator, case_occurrence_time):
        """Filter Cases based on **caseOccurrenceTime** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_occurrence_time (str): The date/time the case occured.
        """
        self._tql.add_filter('caseOccurrenceTime', operator, case_occurrence_time, TQL.Type.STRING)

    def case_occurrence_user(self, operator, case_occurrence_user):
        """Filter Cases based on **caseOccurrenceUser** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_occurrence_user (str): The user who logged the case occurrence time.
        """
        self._tql.add_filter('caseOccurrenceUser', operator, case_occurrence_user, TQL.Type.STRING)

    def case_open_time(self, operator, case_open_time):
        """Filter Cases based on **caseOpenTime** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_open_time (str): The date/time the case was opened.
        """
        self._tql.add_filter('caseOpenTime', operator, case_open_time, TQL.Type.STRING)

    def case_open_user(self, operator, case_open_user):
        """Filter Cases based on **caseOpenUser** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_open_user (str): The user who opened the case.
        """
        self._tql.add_filter('caseOpenUser', operator, case_open_user, TQL.Type.STRING)

    def created_by(self, operator, created_by):
        """Filter Cases based on **createdBy** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            created_by (str): The account login of the user who created the case.
        """
        self._tql.add_filter('createdBy', operator, created_by, TQL.Type.STRING)

    def created_by_id(self, operator, created_by_id):
        """Filter Cases based on **createdById** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            created_by_id (int): The user ID for the creator of the case.
        """
        self._tql.add_filter('createdById', operator, created_by_id, TQL.Type.INTEGER)

    def date_added(self, operator, date_added):
        """Filter Cases based on **dateAdded** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            date_added (str): The date the case was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    def description(self, operator, description):
        """Filter Cases based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of the case.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    @property
    def has_artifact(self):
        """Return **FilterArtifacts** for further filtering."""
        from .artifact import FilterArtifacts

        artifacts = FilterArtifacts(ApiEndpoints.ARTIFACTS, self._tcex, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    def has_group(self, operator, has_group):
        """Filter Cases based on **hasGroup** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            has_group (int): A nested query for association to other buckets.
        """
        self._tql.add_filter('hasGroup', operator, has_group, TQL.Type.INTEGER)

    def has_indicator(self, operator, has_indicator):
        """Filter Cases based on **hasIndicator** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            has_indicator (int): A nested query for association to other indicators.
        """
        self._tql.add_filter('hasIndicator', operator, has_indicator, TQL.Type.INTEGER)

    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        from .note import FilterNotes

        notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    @property
    def has_tag(self):
        """Return **FilterTags** for further filtering."""
        from .tag import FilterTags

        tags = FilterTags(ApiEndpoints.TAGS, self._tcex, TQL())
        self._tql.add_filter('hasTag', TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)
        return tags

    @property
    def has_task(self):
        """Return **FilterTask** for further filtering."""
        from .task import FilterTasks

        tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Cases based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the case.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def id_as_string(self, operator, id_as_string):
        """Filter Cases based on **idAsString** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id_as_string (str): The ID of the case as a String.
        """
        self._tql.add_filter('idAsString', operator, id_as_string, TQL.Type.STRING)

    def name(self, operator, name):
        """Filter Cases based on **name** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            name (str): The name of the case.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def owner(self, operator, owner):
        """Filter Cases based on **owner** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner (int): The Owner ID for the case.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator, owner_name):
        """Filter Cases based on **ownerName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner_name (str): The owner name for the case.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)

    def resolution(self, operator, resolution):
        """Filter Cases based on **resolution** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            resolution (str): The resolution of the case.
        """
        self._tql.add_filter('resolution', operator, resolution, TQL.Type.STRING)

    def severity(self, operator, severity):
        """Filter Cases based on **severity** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            severity (str): The severity of the case.
        """
        self._tql.add_filter('severity', operator, severity, TQL.Type.STRING)

    def status(self, operator, status):
        """Filter Cases based on **status** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            status (str): The status of the case.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def tag(self, operator, tag):
        """Filter Cases based on **tag** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            tag (str): The name of a tag applied to a case.
        """
        self._tql.add_filter('tag', operator, tag, TQL.Type.STRING)

    def target_id(self, operator, target_id):
        """Filter Cases based on **targetId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_id (int): The assigned user or group ID for the case.
        """
        self._tql.add_filter('targetId', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator, target_type):
        """Filter Cases based on **targetType** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_type (str): The target type for this case (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TQL.Type.STRING)

    def xid(self, operator, xid):
        """Filter Cases based on **xid** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            xid (str): The XID of the case.
        """
        self._tql.add_filter('xid', operator, xid, TQL.Type.STRING)

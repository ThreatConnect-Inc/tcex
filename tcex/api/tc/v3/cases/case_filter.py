"""Case TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class CaseFilter(FilterABC):
    """Filter Object for Cases"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.CASES.value

    def assigned_to_user_or_group(self, operator: Enum, assigned_to_user_or_group: str):
        """Filter Assigned To User or Group based on **assignedToUserOrGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            assigned_to_user_or_group: A value of User, Group, or None depending on the assignee.
        """
        self._tql.add_filter(
            'assignedToUserOrGroup', operator, assigned_to_user_or_group, TqlType.STRING
        )

    def assignee_name(self, operator: Enum, assignee_name: str):
        """Filter Assignee based on **assigneeName** keyword.

        Args:
            operator: The operator enum for the filter.
            assignee_name: The user or group name assigned to the Case.
        """
        self._tql.add_filter('assigneeName', operator, assignee_name, TqlType.STRING)

    def attribute(self, operator: Enum, attribute: str):
        """Filter attribute based on **attribute** keyword.

        Args:
            operator: The operator enum for the filter.
            attribute: No description provided.
        """
        self._tql.add_filter('attribute', operator, attribute, TqlType.STRING)

    def case_close_time(self, operator: Enum, case_close_time: str):
        """Filter Case Close Time based on **caseCloseTime** keyword.

        Args:
            operator: The operator enum for the filter.
            case_close_time: The date/time the case was closed.
        """
        case_close_time = self.utils.any_to_datetime(case_close_time).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('caseCloseTime', operator, case_close_time, TqlType.STRING)

    def case_close_user(self, operator: Enum, case_close_user: str):
        """Filter Case Close User based on **caseCloseUser** keyword.

        Args:
            operator: The operator enum for the filter.
            case_close_user: The user who closed the case.
        """
        self._tql.add_filter('caseCloseUser', operator, case_close_user, TqlType.STRING)

    def case_detection_time(self, operator: Enum, case_detection_time: str):
        """Filter Case Detection Time based on **caseDetectionTime** keyword.

        Args:
            operator: The operator enum for the filter.
            case_detection_time: The date/time the case was detected.
        """
        case_detection_time = self.utils.any_to_datetime(case_detection_time).strftime(
            '%Y-%m-%dT%H:%M:%S'
        )
        self._tql.add_filter('caseDetectionTime', operator, case_detection_time, TqlType.STRING)

    def case_detection_user(self, operator: Enum, case_detection_user: str):
        """Filter Case Detection User based on **caseDetectionUser** keyword.

        Args:
            operator: The operator enum for the filter.
            case_detection_user: The user who logged the case detection time.
        """
        self._tql.add_filter('caseDetectionUser', operator, case_detection_user, TqlType.STRING)

    def case_occurrence_time(self, operator: Enum, case_occurrence_time: str):
        """Filter Case Occurrence Time based on **caseOccurrenceTime** keyword.

        Args:
            operator: The operator enum for the filter.
            case_occurrence_time: The date/time the case occurred.
        """
        case_occurrence_time = self.utils.any_to_datetime(case_occurrence_time).strftime(
            '%Y-%m-%dT%H:%M:%S'
        )
        self._tql.add_filter('caseOccurrenceTime', operator, case_occurrence_time, TqlType.STRING)

    def case_occurrence_user(self, operator: Enum, case_occurrence_user: str):
        """Filter Case Occurrence User based on **caseOccurrenceUser** keyword.

        Args:
            operator: The operator enum for the filter.
            case_occurrence_user: The user who logged the case occurrence time.
        """
        self._tql.add_filter('caseOccurrenceUser', operator, case_occurrence_user, TqlType.STRING)

    def case_open_time(self, operator: Enum, case_open_time: str):
        """Filter Case Open Time based on **caseOpenTime** keyword.

        Args:
            operator: The operator enum for the filter.
            case_open_time: The date/time the case was opened.
        """
        case_open_time = self.utils.any_to_datetime(case_open_time).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('caseOpenTime', operator, case_open_time, TqlType.STRING)

    def case_open_user(self, operator: Enum, case_open_user: str):
        """Filter Case Opening User based on **caseOpenUser** keyword.

        Args:
            operator: The operator enum for the filter.
            case_open_user: The user who opened the case.
        """
        self._tql.add_filter('caseOpenUser', operator, case_open_user, TqlType.STRING)

    def created_by(self, operator: Enum, created_by: str):
        """Filter Creator based on **createdBy** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by: The account login of the user who created the case.
        """
        self._tql.add_filter('createdBy', operator, created_by, TqlType.STRING)

    def created_by_id(self, operator: Enum, created_by_id: int):
        """Filter Creator ID based on **createdById** keyword.

        Args:
            operator: The operator enum for the filter.
            created_by_id: The user ID for the creator of the case.
        """
        self._tql.add_filter('createdById', operator, created_by_id, TqlType.INTEGER)

    def date_added(self, operator: Enum, date_added: str):
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the case was added to the system.
        """
        date_added = self.utils.any_to_datetime(date_added).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def description(self, operator: Enum, description: str):
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the case.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    @property
    def has_artifact(self):
        """Return **ArtifactFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter

        artifacts = ArtifactFilter(Tql())
        self._tql.add_filter('hasArtifact', TqlOperator.EQ, artifacts, TqlType.SUB_QUERY)
        return artifacts

    @property
    def has_case(self):
        """Return **CaseFilter** for further filtering."""
        cases = CaseFilter(Tql())
        self._tql.add_filter('hasCase', TqlOperator.EQ, cases, TqlType.SUB_QUERY)
        return cases

    @property
    def has_group(self):
        """Return **GroupFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.groups.group_filter import GroupFilter

        groups = GroupFilter(Tql())
        self._tql.add_filter('hasGroup', TqlOperator.EQ, groups, TqlType.SUB_QUERY)
        return groups

    @property
    def has_indicator(self):
        """Return **IndicatorFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter

        indicators = IndicatorFilter(Tql())
        self._tql.add_filter('hasIndicator', TqlOperator.EQ, indicators, TqlType.SUB_QUERY)
        return indicators

    @property
    def has_note(self):
        """Return **NoteFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.notes.note_filter import NoteFilter

        notes = NoteFilter(Tql())
        self._tql.add_filter('hasNote', TqlOperator.EQ, notes, TqlType.SUB_QUERY)
        return notes

    @property
    def has_tag(self):
        """Return **TagFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tags.tag_filter import TagFilter

        tags = TagFilter(Tql())
        self._tql.add_filter('hasTag', TqlOperator.EQ, tags, TqlType.SUB_QUERY)
        return tags

    @property
    def has_task(self):
        """Return **TaskFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tasks.task_filter import TaskFilter

        tasks = TaskFilter(Tql())
        self._tql.add_filter('hasTask', TqlOperator.EQ, tasks, TqlType.SUB_QUERY)
        return tasks

    def has_workflow_template(self, operator: Enum, has_workflow_template: int):
        """Filter Associated Workflow Template based on **hasWorkflowTemplate** keyword.

        Args:
            operator: The operator enum for the filter.
            has_workflow_template: A nested query for association to workflow templates.
        """
        self._tql.add_filter(
            'hasWorkflowTemplate', operator, has_workflow_template, TqlType.INTEGER
        )

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the case.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def id_as_string(self, operator: Enum, id_as_string: str):
        """Filter ID As String based on **idAsString** keyword.

        Args:
            operator: The operator enum for the filter.
            id_as_string: The ID of the case as a String.
        """
        self._tql.add_filter('idAsString', operator, id_as_string, TqlType.STRING)

    def name(self, operator: Enum, name: str):
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the case.
        """
        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def owner(self, operator: Enum, owner: int):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the case.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name for the case.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def resolution(self, operator: Enum, resolution: str):
        """Filter Resolution based on **resolution** keyword.

        Args:
            operator: The operator enum for the filter.
            resolution: The resolution of the case.
        """
        self._tql.add_filter('resolution', operator, resolution, TqlType.STRING)

    def severity(self, operator: Enum, severity: str):
        """Filter Severity based on **severity** keyword.

        Args:
            operator: The operator enum for the filter.
            severity: The severity of the case.
        """
        self._tql.add_filter('severity', operator, severity, TqlType.STRING)

    def status(self, operator: Enum, status: str):
        """Filter Status based on **status** keyword.

        Args:
            operator: The operator enum for the filter.
            status: The status of the case.
        """
        self._tql.add_filter('status', operator, status, TqlType.STRING)

    def tag(self, operator: Enum, tag: str):
        """Filter Tag based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to a case.
        """
        self._tql.add_filter('tag', operator, tag, TqlType.STRING)

    def target_id(self, operator: Enum, target_id: int):
        """Filter Assignee ID based on **targetId** keyword.

        Args:
            operator: The operator enum for the filter.
            target_id: The assigned user or group ID for the case.
        """
        self._tql.add_filter('targetId', operator, target_id, TqlType.INTEGER)

    def target_type(self, operator: Enum, target_type: str):
        """Filter Target Type based on **targetType** keyword.

        Args:
            operator: The operator enum for the filter.
            target_type: The target type for this case (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TqlType.STRING)

    def type_name(self, operator: Enum, type_name: str):
        """Filter Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the case.
        """
        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)

    def xid(self, operator: Enum, xid: str):
        """Filter XID based on **xid** keyword.

        Args:
            operator: The operator enum for the filter.
            xid: The XID of the case.
        """
        self._tql.add_filter('xid', operator, xid, TqlType.STRING)

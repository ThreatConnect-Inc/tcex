"""Task Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class FilterTask(FilterABC):
    """Filter Object for Tasks"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TASKS.value

    def automated(self, operator, automated):
        """Filter Tasks based on **automated** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            automated (bool): A flag indicating whether or not the task is automated.
        """
        self._tql.add_filter('automated', operator, automated, TQL.Type.BOOLEAN)

    def case_id(self, operator, case_id):
        """Filter Tasks based on **caseId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case this Task is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def case_severity(self, operator, case_severity):
        """Filter Tasks based on **caseSeverity** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_severity (str): The severity of the case associated with the task.
        """
        self._tql.add_filter('caseSeverity', operator, case_severity, TQL.Type.STRING)

    def completed_by(self, operator, completed_by):
        """Filter Tasks based on **completedBy** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            completed_by (str): The account login of the user who completed the task.
        """
        self._tql.add_filter('completedBy', operator, completed_by, TQL.Type.STRING)

    def completed_date(self, operator, completed_date):
        """Filter Tasks based on **completedDate** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            completed_date (str): The completion date for the task.
        """
        self._tql.add_filter('completedDate', operator, completed_date, TQL.Type.STRING)

    def description(self, operator, description):
        """Filter Tasks based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of the task.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    def due_date(self, operator, due_date):
        """Filter Tasks based on **dueDate** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            due_date (str): The due date for the task.
        """
        self._tql.add_filter('dueDate', operator, due_date, TQL.Type.STRING)

    # TODO: [low] cyclic import typing
    @property
    def has_artifact(self):  # pragma: no cover
        """Return **FilterArtifacts** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_artifact import FilterArtifact

        artifacts = FilterArtifact(self._session, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    # TODO: [low] cyclic import typing
    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_case import FilterCase

        cases = FilterCase(self._session, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    # TODO: [low] cyclic import typing
    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_note import FilterNote

        notes = FilterNote(self._session, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Tasks based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the task.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name(self, operator, name):
        """Filter Tasks based on **name** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            name (str): The name of the task.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def required(self, operator, required):
        """Filter Tasks based on **required** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            required (bool): Flag indicating whether or not the task is required.
        """
        self._tql.add_filter('required', operator, required, TQL.Type.BOOLEAN)

    def status(self, operator, status):
        """Filter Tasks based on **status** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            status (str): The status of the task.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def target_id(self, operator, target_id):
        """Filter Tasks based on **targetId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_id (int): The assigned user or group ID for the task.
        """
        self._tql.add_filter('targetId', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator, target_type):
        """Filter Tasks based on **targetType** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_type (str): The target type for this task (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TQL.Type.STRING)

    def workflow_phase(self, operator, workflow_phase):
        """Filter Tasks based on **workflowPhase** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            workflow_phase (int): The workflow phase of the task.
        """
        self._tql.add_filter('workflowPhase', operator, workflow_phase, TQL.Type.INTEGER)

    def workflow_step(self, operator, workflow_step):
        """Filter Tasks based on **workflowStep** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            workflow_step (int): The workflow step of the task.
        """
        self._tql.add_filter('workflowStep', operator, workflow_step, TQL.Type.INTEGER)

    def xid(self, operator: Enum, xid):
        """Filter Tasks based on **xid** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            xid (str): The XID of the task.
        """
        self._tql.add_filter('xid', operator, xid, TQL.Type.STRING)

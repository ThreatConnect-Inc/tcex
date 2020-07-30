# -*- coding: utf-8 -*-
"""ThreatConnect Case Management"""
from .artifact import Artifact, Artifacts
from .artifact_type import ArtifactType, ArtifactTypes
from .assignee import Assignee, User, Users
from .case import Case, Cases
from .note import Note, Notes
from .tag import Tag, Tags
from .task import Task, Tasks
from .workflow_event import WorkflowEvent, WorkflowEvents
from .workflow_template import WorkflowTemplate, WorkflowTemplates


class CaseManagement:
    """Case Management Class for TcEx

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
    """

    def __init__(self, tcex):
        """Initialize Class properties."""
        self.tcex = tcex

    def artifact(self, **kwargs):
        """Return a instance of Artifact object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            analytics_priority (str, kwargs): [Read-Only] The **Analytics Priority**
                for the Artifact.
            analytics_priority_level (int, kwargs): [Read-Only] The **Analytics Priority Level** for
                the Artifact.
            analytics_score (int, kwargs): [Read-Only] The **Analytics Score** for the Artifact.
            analytics_status (int, kwargs): [Read-Only] The **Analytics Status** for the Artifact.
            analytics_type (str, kwargs): [Read-Only] The **Analytics Type** for the Artifact.
            artifact_type (ArtifactType, kwargs): [Read-Only] The **Artifact Type**
                for the Artifact.
            case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Artifact.
            case_xid (str, kwargs): [Required (alt: caseId)] The **Case Xid** for the Artifact.
            date_added (str, kwargs): [Read-Only] The **Date Added** for the Artifact.
            file_data (str, kwargs): Base64 encoded file attachment required only for certain
                artifact types
            intel_type (str, kwargs): The **Intel Type** for the Artifact.
            links (Link, kwargs): The **Links** for the Artifact.
            notes (Note, kwargs): a list of Notes corresponding to the Artifact
            parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Artifact.
            source (str, kwargs): The **Source** for the Artifact.
            summary (str, kwargs): [Required] The **Summary** for the Artifact.
            task (case_management.task.Task, kwargs): [Read-Only] The **Task** for the Artifact.
            task_id (int, kwargs): the ID of the task which the Artifact references
            task_xid (str, kwargs): the XID of the task which the Artifact references
            type (str, kwargs): [Required] The **Type** for the Artifact.
        """
        return Artifact(self.tcex, **kwargs)

    def artifacts(self, **kwargs):
        """Return a instance of Artifacts object.

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
                retrieving the Artifacts objects.
        """
        return Artifacts(self.tcex, **kwargs)

    def artifact_type(self, **kwargs):
        """Return a instance of Artifact Type object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            data_type (str, kwargs): [Read-Only] The **Data Type** for the Artifact Type.
            description (str, kwargs): [Read-Only] The **Description** for the Artifact Type.
            intel_type (str, kwargs): [Read-Only] The **Intel Type** for the Artifact Type.
            name (str, kwargs): [Read-Only] The **Name** for the Artifact Type.
        """
        return ArtifactType(self.tcex, **kwargs)

    def artifact_types(self, **kwargs):
        """Return a instance of Artifact Types object.

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
            params(dict, optional): Dict of the params to be sent
                while retrieving the Artifact Type objects.
        """
        return ArtifactTypes(self.tcex, **kwargs)

    @staticmethod
    def assignee(**kwargs):
        """Return a instance of Assignee object.

        For User type the user_name or id fields is required and
        for the Group type the name or id is required.

        Args:
            first_name (str, kwargs): The first name of the User.
            id (id, kwargs): The id of the User.
            name (str, kwargs): The name of the Group.
            last_name (str, kwargs): The last name of the user.
            pseudonym (str, kwargs): The pseudonym of the User.
            role (str, kwargs): The role of the User.
            user_name (str, kwargs): The user name of the User.
            type (str, kwargs): The assignee type. Default to User.
        """
        return Assignee(**kwargs)

    def case(self, **kwargs):
        """Return a instance of Case object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            artifacts (Artifact, kwargs): a list of Artifacts corresponding to the Case
            assignee (Assignee, kwargs): the user or group Assignee object for the Case
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
            tags (tcex.case_management.tag.Tag, kwargs): a list of Tags corresponding to the Case
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
        return Case(self.tcex, **kwargs)

    def cases(self, **kwargs):
        """Return a instance of Cases object.

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
        return Cases(self.tcex, **kwargs)

    def create_entity(self, entity, owner):
        """Create a CM object provided a dict and owner."""
        entity_type = entity.get('type').lower()
        entity_type = entity_type.replace(' ', '_')
        try:
            obj = getattr(self, entity_type)(**entity)
        except AttributeError:
            return None

        r = obj.submit()
        data = {'status_code': r.status_code}
        if r.ok:
            data.update(r.json().get('data', {}))
            data['main_type'] = 'Case_Management'
            data['sub_type'] = entity_type
            data['owner'] = owner

        return data

    def note(self, **kwargs):
        """Return a instance of Note object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            artifact (Artifact, kwargs): [Read-Only] The **Artifact** for the Note.
            artifact_id (int, kwargs): the ID of the Artifact on which to apply the Note
            author (int, kwargs): [Read-Only] The **Author** for the Note.
            case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Note.
            case_xid (str, kwargs): [Required (alt: caseId)]
            date_added (str, kwargs): [Read-Only] The **Date Added** for the Note.
            edited (boolean, kwargs): [Read-Only] The **Edited** for the Note.
            last_modified (str, kwargs): [Read-Only] The **Last Modified** for the Note.
            parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Note.
            summary (str, kwargs): [Read-Only] The **Summary** for the Note.
            task (case_management.task.Task, kwargs): [Read-Only] The **Task** for the Note.
            task_id (int, kwargs): the ID of the Task on which to apply the Note
            task_xid (str, kwargs): the XID of the Task on which to apply the Note
            text (str, kwargs): [Required] The **Text** for the Note.
            workflow_event (WorkflowEvent, kwargs): [Read-Only] The **Workflow Event** for the Note.
            workflow_event_id (int, kwargs): the ID of the Event on which to apply the Note
        """
        return Note(self.tcex, **kwargs)

    def notes(self, **kwargs):
        """Return a instance of Notes object.

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
                Case Object for Note. Defaults to None.
            tql_filters (list, optional): List of TQL filters. Defaults to None.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Notes objects.
        """
        return Notes(self.tcex, **kwargs)

    def tag(self, **kwargs):
        """Return a instance of Tag object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            cases (Case, kwargs): [Read-Only] The **Cases** for the Tag.
            description (str, kwargs): a brief description of the Tag
            last_used (str, kwargs): [Read-Only] The **Last Used** for the Tag.
            name (str, kwargs): [Required] The **Name** for the Tag.
            owner (str, kwargs): [Read-Only] The **Owner** for the Tag.
        """
        return Tag(self.tcex, **kwargs)

    def tags(self, **kwargs):
        """Return a instance of Tags object.

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
                Case Object for Tag. Defaults to None.
            tql_filters (list, optional): List of TQL filters. Defaults to None.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Tag objects.
        """
        return Tags(self.tcex, **kwargs)

    def task(self, **kwargs):
        """Return a instance of Task object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            artifacts (Artifact, kwargs): a list of Artifacts corresponding to the Task
            assignee (Assignee, kwargs): the user or group Assignee object for the Task
            case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Task.
            case_xid (str, kwargs): [Required (alt: caseId)] The **Case Xid** for the Task.
            completed_by (str, kwargs): [Read-Only] The **Completed By** for the Task.
            completed_date (str, kwargs): the completion date of the Task
            config_playbook (str, kwargs): [Read-Only] The **Config Playbook** for the Task.
            config_task (dict, kwargs): [Read-Only] The **Config Task** for the Task.
            dependent_on_id (str, kwargs): [Read-Only] The **Dependent On ID** for the Task.
            description (str, kwargs): The **Description** for the Task.
            due_date (str, kwargs): the due date of the Task
            duration (int, kwargs): [Read-Only] The **Duration** for the Task.
            id_dependent_on (int, kwargs): [Read-Only] The **Id_Dependent On** for the Task.
            name (str, kwargs): [Required] The **Name** for the Task.
            notes (Note, kwargs): a list of Notes corresponding to the Task
            parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Task.
            required (bool, kwargs): [Read-Only] The **Required** flag for the Task.
            status (str, kwargs): The **Status** for the Task.
            workflow_phase (int, kwargs): the phase of the workflow
            workflow_step (int, kwargs): the step of the workflow
            xid (str, kwargs): The **Xid** for the Task.
        """
        return Task(self.tcex, **kwargs)

    def tasks(self, **kwargs):
        """Return a instance of Tasks object.

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
                Case Object for Task. Defaults to None.
            tql_filters (list, optional): List of TQL filters. Defaults to None.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Task objects.
        """
        return Tasks(self.tcex, **kwargs)

    @staticmethod
    def user(**kwargs):
        """Return a instance of User object.

        Args:
            first_name (str, kwargs): The first name of the user.
            id (id, kwargs): The id of the user.
            last_name (str, kwargs): The last name of the user.
            pseudonym (str, kwargs): The pseudonym of the user.
            role (str, kwargs): The role of the user.
            user_name (str, kwargs): The user name of the user.
        """
        return User(**kwargs)

    @staticmethod
    def users(users):
        """Sub class of the Cases object. Used to map the users to.

        Args:
            users (list): A array of user data
        """
        return Users(users)

    def workflow_event(self, **kwargs):
        """Return a instance of Workflow Event object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Workflow Event.
            case_xid (str, kwargs): [Required (alt: caseId)] The **Case Xid**
                for the Workflow Event.
            date_added (str, kwargs): [Read-Only] The **Date Added** for the Workflow Event.
            deleted (bool, kwargs): [Read-Only] The **Deleted** flag for the Workflow Event.
            deleted_reason (str, kwargs): the reason for deleting the event (required
                input for DELETE operation only)
            event_date (str, kwargs): the time that the Event is logged
            link (str, kwargs): [Read-Only] The **Link** for the Workflow Event.
            link_text (str, kwargs): [Read-Only] The **Link Text** for the Workflow Event.
            notes (Note, kwargs): a list of Notes corresponding to the Event
            parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Workflow Event.
            summary (str, kwargs): [Required] The **Summary** for the Workflow Event.
            system_generated (bool, kwargs): [Read-Only] The **System Generated**
                flag for the Workflow Event.
            user (User, kwargs): [Read-Only] The **User** for the Workflow Event.
        """
        return WorkflowEvent(self.tcex, **kwargs)

    def workflow_events(self, **kwargs):
        """Return a instance of Workflow Events object.

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
                retrieving the Workflow Event objects.
        """
        return WorkflowEvents(self.tcex, **kwargs)

    def workflow_template(self, **kwargs):
        """Return a instance of Workflow Template object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            active (bool, kwargs): [Read-Only] The **Active** flag for the Workflow Template.
            assignee (Assignee, kwargs): [Read-Only] The **Assignee** for the Workflow Template.
            cases (Case, kwargs): [Read-Only] The **Cases** for the Workflow Template.
            config_artifact (str, kwargs): [Read-Only] The **Config Artifact** for the Workflow
                Template.
            config_playbook (str, kwargs): [Read-Only] The **Config Playbook** for the Workflow
                Template.
            config_task (dict, kwargs): [Read-Only] The **Config Task** for the Workflow Template.
            description (str, kwargs): The **Description** for the Workflow Template.
            name (str, kwargs): [Required] The **Name** for the Workflow Template.
            target_type (str, kwargs): [Read-Only] The **Target Type** for the Workflow Template.
            version (int, kwargs): The **Version** for the Workflow Template.
        """
        return WorkflowTemplate(self.tcex, **kwargs)

    def workflow_templates(self, **kwargs):
        """Return a instance of Workflow Templates object.

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
                Case Object for Workflow Template. Defaults to None.
            tql_filters (list, optional): List of TQL filters. Defaults to None.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Workflow Event objects.
        """
        return WorkflowTemplates(self.tcex, **kwargs)

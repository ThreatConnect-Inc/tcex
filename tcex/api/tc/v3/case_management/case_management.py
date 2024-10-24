"""TcEx Framework Module"""

# third-party
from requests import Session

# first-party
from tcex.api.tc.v3.case_attributes.case_attribute import CaseAttribute, CaseAttributes


class CaseManagement:
    """Case Management

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session):
        """Initialize instance properties."""
        self.session = session

    def artifact(self, **kwargs) -> 'Artifact':
        """Return a instance of Artifact object.

        Model Schema:
        >>> from tcex.api.tc.v3.case_management.model.artifact_model import ArtifactModel
        >>> print(ArtifactModel.schema_json(by_alias=False, indent=2))

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            case_id (int, kwargs): The **case id** for the Artifact.
            case_xid (str, kwargs): The **case xid** for the Artifact.
            derived_link (bool, kwargs): Flag to specify if this artifact should be used for
                potentially associated cases or not.
            file_data (str, kwargs): Base64 encoded file attachment required only for certain
                artifact types.
            hash_code (str, kwargs): Hashcode of Artifact of type File.
            notes (Note, kwargs): A list of Notes corresponding to the Artifact.
            source (str, kwargs): The **source** for the Artifact.
            summary (str, kwargs): The **summary** for the Artifact.
            task_id (int, kwargs): The ID of the task which the Artifact references.
            task_xid (str, kwargs): The XID of the task which the Artifact references.
            type (str, kwargs): The **type** for the Artifact.
        """
        return Artifact(session=self.session, **kwargs)

    def artifacts(self, **kwargs) -> 'Artifacts':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Artifact.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return Artifacts(session=self.session, **kwargs)

    def artifact_type(self, **kwargs) -> 'ArtifactType':
        """Return a instance of Artifact Type object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            data_type (str, kwargs): [Read-Only] The **Data Type** for the Artifact Type.
            description (str, kwargs): [Read-Only] The **Description** for the Artifact Type.
            intel_type (str, kwargs): [Read-Only] The **Intel Type** for the Artifact Type.
            name (str, kwargs): [Read-Only] The **Name** for the Artifact Type.
        """
        return ArtifactType(session=self.session, **kwargs)

    def artifact_types(self, **kwargs) -> 'ArtifactTypes':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            initial_response (dict, optional): Initial data in
                Case Object for Artifact.
            tql_filters (list, optional): List of TQL filters.
            params(dict, optional): Dict of the params to be sent
                while retrieving the Artifact Type objects.
        """
        return ArtifactTypes(session=self.session, **kwargs)

    def case(self, **kwargs) -> 'Case':
        """Return a instance of Case object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            artifacts (Artifacts, kwargs): A list of Artifacts corresponding to the Case.
            assignee (Assignee, kwargs): The user or group Assignee object for the Case.
            description (str, kwargs): The **description** for the Case.
            name (str, kwargs): The **name** for the Case.
            notes (Notes, kwargs): A list of Notes corresponding to the Case.
            resolution (str, kwargs): The **resolution** for the Case.
            severity (str, kwargs): The **severity** for the Case.
            status (str, kwargs): The **status** for the Case.
            tags (Notes, kwargs): A list of Tags corresponding to the Case (NOTE: Setting this
                parameter will replace any existing tag(s) with the one(s) specified).
            tasks (Tasks, kwargs): A list of Tasks corresponding to the Case.
            user_access (Users, kwargs): A list of Users that, when defined, are the only ones
                allowed to view or edit the Case.
            workflow_events (WorkflowEvents, kwargs): A list of workflowEvents (timeline)
                corresponding to the Case.
            workflow_template (WorkflowTemplate, kwargs): The Template that the Case is populated
                by.
            xid (str, kwargs): The **xid** for the Case.
        """
        return Case(session=self.session, **kwargs)

    def case_attribute(self, **kwargs) -> CaseAttribute:
        """Return a instance of Case Attributes object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            case_id (int, kwargs): Case associated with attribute.
            default (bool, kwargs): A flag indicating that this is the default attribute of its type
                within the object. Only applies to certain attribute and data types.
            source (str, kwargs): The attribute source.
            type (str, kwargs): The attribute type.
            value (str, kwargs): Attribute value.
        """
        return CaseAttribute(session=self.session, **kwargs)

    def case_attributes(self, **kwargs) -> CaseAttributes:
        """Return a instance of Case Attributes object.

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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Group.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return CaseAttributes(session=self.session, **kwargs)

    def cases(self, **kwargs) -> 'Cases':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            initial_response (dict, optional): Initial data in
                Case Object for Artifact.
            tql_filters (list, optional): List of TQL filters.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Case objects.
        """
        return Cases(session=self.session, **kwargs)

    def create_entity(self, entity: dict, owner: str) -> dict | None:
        """Create a CM object provided a dict and owner."""
        entity_type = entity.pop('type').lower()
        entity_type = entity_type.replace(' ', '_')
        try:
            obj = getattr(self, entity_type)(**entity)
        except AttributeError:
            return None

        obj.create()
        data = {'status_code': obj.request.status_code}
        if obj.request.ok:
            data.update(obj.request.json().get('data', {}))
            data['main_type'] = 'Case_Management'
            data['sub_type'] = entity_type
            data['owner'] = owner

        return data

    def note(self, **kwargs) -> 'Note':
        """Return a instance of Note object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
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
            task (Task, kwargs): [Read-Only] The **Task** for the Note.
            task_id (int, kwargs): the ID of the Task on which to apply the Note
            task_xid (str, kwargs): the XID of the Task on which to apply the Note
            text (str, kwargs): [Required] The **Text** for the Note.
            workflow_event (WorkflowEvent, kwargs): [Read-Only] The **Workflow Event** for the Note.
            workflow_event_id (int, kwargs): the ID of the Event on which to apply the Note
        """
        return Note(session=self.session, **kwargs)

    def notes(self, **kwargs) -> 'Notes':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            initial_response (dict, optional): Initial data in
                Case Object for Note.
            tql_filters (list, optional): List of TQL filters.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Notes objects.
        """
        return Notes(session=self.session, **kwargs)

    def tag(self, **kwargs) -> 'Tag':
        """Return a instance of Tag object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            cases (Case, kwargs): [Read-Only] The **Cases** for the Tag.
            description (str, kwargs): a brief description of the Tag
            last_used (str, kwargs): [Read-Only] The **Last Used** for the Tag.
            name (str, kwargs): [Required] The **Name** for the Tag.
            owner (str, kwargs): [Read-Only] The **Owner** for the Tag.
        """
        return Tag(session=self.session, **kwargs)

    def tags(self, **kwargs) -> 'Tags':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            initial_response (dict, optional): Initial data in
                Case Object for Tag.
            tql_filters (list, optional): List of TQL filters.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Tag objects.
        """
        return Tags(session=self.session, **kwargs)

    def task(self, **kwargs) -> 'Task':
        """Return a instance of Task object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
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
        return Task(session=self.session, **kwargs)

    def tasks(self, **kwargs) -> 'Tasks':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            initial_response (dict, optional): Initial data in
                Case Object for Task.
            tql_filters (list, optional): List of TQL filters.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Task objects.
        """
        return Tasks(session=self.session, **kwargs)

    def workflow_event(self, **kwargs) -> 'WorkflowEvent':
        """Return a instance of Workflow Event object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
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
        return WorkflowEvent(session=self.session, **kwargs)

    def workflow_events(self, **kwargs) -> 'WorkflowEvents':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            initial_response (dict, optional): Initial data in
                Case Object for Artifact.
            tql_filters (list, optional): List of TQL filters.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Workflow Event objects.
        """
        return WorkflowEvents(session=self.session, **kwargs)

    def workflow_template(self, **kwargs) -> 'WorkflowTemplate':
        """Return a instance of Workflow Template object.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            **kwargs: Additional keyword arguments.

        Keyword Args:
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
        return WorkflowTemplate(session=self.session, **kwargs)

    def workflow_templates(self, **kwargs) -> 'WorkflowTemplates':
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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            initial_response (dict, optional): Initial data in
                Case Object for Workflow Template.
            tql_filters (list, optional): List of TQL filters.
            params(dict, optional): Dict of the params to be sent while
                retrieving the Workflow Event objects.
        """
        return WorkflowTemplates(session=self.session, **kwargs)


# first-party
# pylint: disable=wrong-import-position
from tcex.api.tc.v3.artifact_types.artifact_type import ArtifactType, ArtifactTypes
from tcex.api.tc.v3.artifacts.artifact import Artifact, Artifacts
from tcex.api.tc.v3.cases.case import Case, Cases
from tcex.api.tc.v3.notes.note import Note, Notes
from tcex.api.tc.v3.tags.tag import Tag, Tags
from tcex.api.tc.v3.tasks.task import Task, Tasks
from tcex.api.tc.v3.workflow_events.workflow_event import WorkflowEvent, WorkflowEvents
from tcex.api.tc.v3.workflow_templates.workflow_template import WorkflowTemplate, WorkflowTemplates

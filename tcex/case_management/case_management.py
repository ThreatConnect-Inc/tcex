# -*- coding: utf-8 -*-
"""ThreatConnect Case Management"""
from .assignee import Assignee, User, Users
from .artifact import Artifact, Artifacts
from .artifact_type import ArtifactType, ArtifactTypes
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
        """Return a instance of Artifact object."""
        return Artifact(self.tcex, **kwargs)

    def artifacts(self, **kwargs):
        """Return a instance of Artifacts object."""
        return Artifacts(self.tcex, **kwargs)

    def artifact_type(self, **kwargs):
        """Return a instance of Artifact Type object."""
        return ArtifactType(self.tcex, **kwargs)

    def artifact_types(self, **kwargs):
        """Return a instance of Artifact Types object."""
        return ArtifactTypes(self.tcex, **kwargs)

    @staticmethod
    def assignee(**kwargs):
        """Return a instance of Assignee object."""
        return Assignee(**kwargs)

    def case(self, **kwargs):
        """Return a instance of Case object."""
        return Case(self.tcex, **kwargs)

    def cases(self, **kwargs):
        """Return a instance of Cases object."""
        return Cases(self.tcex, **kwargs)

    def create_entity(self, entity, owner):
        """Create a CM object provided a dict and owner."""
        entity_type = entity.get('type').lower()
        obj = getattr(self, entity_type)
        if obj is None:
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
        """Return a instance of Note object."""
        return Note(self.tcex, **kwargs)

    def notes(self, **kwargs):
        """Return a instance of Notes object."""
        return Notes(self.tcex, **kwargs)

    def tag(self, **kwargs):
        """Return a instance of Tag object."""
        return Tag(self.tcex, **kwargs)

    def tags(self, **kwargs):
        """Return a instance of Tags object."""
        return Tags(self.tcex, **kwargs)

    def task(self, **kwargs):
        """Return a instance of Task object."""
        return Task(self.tcex, **kwargs)

    def tasks(self, **kwargs):
        """Return a instance of Tasks object."""
        return Tasks(self.tcex, **kwargs)

    @staticmethod
    def user(**kwargs):
        """Return a instance of User object."""
        return User(**kwargs)

    @staticmethod
    def users(**kwargs):
        """Return a instance of Users object."""
        return Users(**kwargs)

    def workflow_event(self, **kwargs):
        """Return a instance of Workflow Event object."""
        return WorkflowEvent(self.tcex, **kwargs)

    def workflow_events(self, **kwargs):
        """Return a instance of Workflow Events object."""
        return WorkflowEvents(self.tcex, **kwargs)

    def workflow_template(self, **kwargs):
        """Return a instance of Workflow Template object."""
        return WorkflowTemplate(self.tcex, **kwargs)

    def workflow_templates(self, **kwargs):
        """Return a instance of Workflow Templates object."""
        return WorkflowTemplates(self.tcex, **kwargs)

# -*- coding: utf-8 -*-
from .artifact import Artifact, Artifacts
from .artifact_type import ArtifactType, ArtifactTypes
from .case import Case, Cases
from .task import Task, Tasks
from .note import Note, Notes
from .tag import Tag, Tags
from .workflow_event import WorkflowEvent, WorkflowEvents
from .workflow_template import WorkflowTemplate, WorkflowTemplates


class CaseManagement(object):
    def __init__(self, tcex):
        """
        Args:
            tcex (obj): An instance of TcEx.
        """
        self.tcex = tcex

    def artifacts(self, **kwargs):
        return Artifacts(self.tcex, **kwargs)

    def artifact(self, **kwargs):
        return Artifact(self.tcex, **kwargs)

    def artifact_types(self, **kwargs):
        return ArtifactTypes(self.tcex, **kwargs)

    def artifact_type(self, **kwargs):
        return ArtifactType(self.tcex, **kwargs)

    def cases(self, **kwargs):
        return Cases(self.tcex, **kwargs)

    def case(self, **kwargs):
        return Case(self.tcex, **kwargs)

    def note(self, **kwargs):
        return Note(self.tcex, **kwargs)

    def notes(self, **kwargs):
        return Notes(self.tcex, **kwargs)

    def task(self, **kwargs):
        return Task(self.tcex, **kwargs)

    def tasks(self, **kwargs):
        return Tasks(self.tcex, **kwargs)

    def workflow_event(self, **kwargs):
        return WorkflowEvent(self.tcex, **kwargs)

    def workflow_events(self, **kwargs):
        return WorkflowEvents(self.tcex, **kwargs)

    def workflow_template(self, **kwargs):
        return WorkflowTemplate(self.tcex, **kwargs)

    def workflow_templates(self, **kwargs):
        return WorkflowTemplates(self.tcex, **kwargs)

    def tag(self, **kwargs):
        return Tag(self.tcex, **kwargs)

    def tags(self, **kwargs):
        return Tags(self.tcex, **kwargs)

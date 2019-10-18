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

    def artifacts(self):
        return Artifacts(self.tcex)

    def artifact(self):
        return Artifact(self.tcex)

    def artifact_types(self):
        return ArtifactTypes(self.tcex)

    def artifact_type(self):
        return ArtifactType(self.tcex)

    def cases(self):
        return Cases(self.tcex)

    def case(self, **kwargs):
        return Case(self.tcex, **kwargs)

    def note(self):
        return Note(self.tcex)

    def notes(self):
        return Notes(self.tcex)

    def task(self):
        return Task(self.tcex)

    def tasks(self):
        return Tasks(self.tcex)

    def workflow_event(self):
        return WorkflowEvent(self.tcex)

    def workflow_events(self):
        return WorkflowEvents(self.tcex)

    def workflow_template(self):
        return WorkflowTemplate(self.tcex)

    def workflow_templates(self):
        return WorkflowTemplates(self.tcex)

    def tag(self):
        return Tag(self.tcex)

    def tags(self):
        return Tags(self.tcex)

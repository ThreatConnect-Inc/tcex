# -*- coding: utf-8 -*-
from .artifact import Artifact
from .artifacts import Artifacts
from .artifact_type import ArtifactType
from .case import Case
from .task import Task
from .note import Note
from .tag import Tag
from .workflow_event import WorkflowEvent
from .workflow_template import WorkflowTemplate


class CaseManagement(object):
    def artifacts(self):
        return Artifacts()

    def artifact(self):
        return Artifact()

    def artifact_types(self):
        return ArtifactTypes()

    def artifact_type(self):
        return ArtifactType()

    def cases(self):
        return Cases()

    def case(self):
        return Case()

    def note(self):
        return Note()

    def notes(self):
        return Notes()

    def task(self):
        return Task()

    def tasks(self):
        return Tasks()

    def workflow_event(self):
        return WorkflowEvent()

    def workflow_events(self):
        return WorkflowEvents()

    def workflow_templates(self):
        return WorkflowTemplate()

    def workflow_templates(self):
        return WorkflowTemplates()

    def tag(self):
        return Tag()

    def tags(self):
        return Tags()


# artifact = self.tcex.v3.cm.add_artifact(count, date_observed)
#
# this will return a tiny artifact object using the __stub__ feature.
#
# then the user would
#
# artifact.submit()

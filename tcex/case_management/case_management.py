# -*- coding: utf-8 -*-
from .artifact import Artifact, Artifacts
from .artifact_type import ArtifactType, ArtifactTypes
from .case import Case, Cases
from .task import Task, Tasks
from .note import Note, Notes
from .tag import Tag, Tags
from .workflow_event import WorkflowEvent, WorkflowEvents
from .workflow_template import WorkflowTemplate, WorkflowTemplates
import requests


class CaseManagement(object):
    def __init__(self, tcex):
        """
        Initialize CaseManagement Class.

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

    def obj_from_type(self, obj_type):
        obj_type = obj_type.lower()
        if obj_type == 'tag':
            return Tag(self.tcex, **{})
        elif obj_type == 'case':
            return Case(self.tcex, **{})
        elif obj_type == 'note':
            return Note(self.tcex, **{})
        elif obj_type == 'artifact':
            return Artifact(self.tcex, **{})
        elif obj_type == 'task':
            return Task(self.tcex, **{})
        elif obj_type in ['workflow_event', 'workflowevent', 'workflow event']:
            return WorkflowEvent(self.tcex, **{})
        elif obj_type in ['workflow_template', 'workflowtemplate', 'workflow template']:
            return WorkflowTemplate(self.tcex, **{})

        return None

    def obj_from_entity(self, entity):
        obj_type = entity.pop('type').lower()
        if obj_type == 'tag':
            return Tag(self.tcex, **entity)
        elif obj_type == 'case':
            return Case(self.tcex, **entity)
        elif obj_type == 'note':
            return Note(self.tcex, **entity)
        elif obj_type == 'artifact':
            return Artifact(self.tcex, **entity)
        elif obj_type == 'task':
            return Task(self.tcex, **entity)
        elif obj_type in ['workflow_event', 'workflowevent', 'workflow event']:
            return WorkflowEvent(self.tcex, **entity)
        elif obj_type in ['workflow_template', 'workflowtemplate', 'workflow template']:
            return WorkflowTemplate(self.tcex, **entity)

        return None

    def create_entity(self, entity, owner):
        entity_type = entity.get('type').lower()
        obj = self.obj_from_entity(entity)
        if obj is None:
            return None

        r = obj.submit()
        response = {}
        if isinstance(r, requests.models.Response):
            response['status_code'] = r.status_code
        else:
            response['status_code'] = 201
            response['unique_id'] = r.as_dict.get('id')

        response['main_type'] = 'Case_Management'
        response['sub_type'] = entity_type
        response['owner'] = owner

        return response

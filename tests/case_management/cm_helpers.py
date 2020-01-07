# -*- coding: utf-8 -*-
"""Case Management PyTest Helper Method"""
import inspect
from random import randint

# from tcex.case_management.tql import TQL


class CMHelper:
    """Case Management Helper Module

    Args:
        cm (tcex.CaseManagement): A instantiated TC CaseManagement Object
    """

    def __init__(self, cm):
        """Initialize Class Properties"""
        self.cm = cm

        # cleanup values
        self.cases = []

    def create_case(self, **kwargs):
        """Create an case.

        If a case_name is not provide a dynamic case name will be used.

        Args:
            name (str, kwargs): Optional case name.
            severity (str, kwargs): Optional case severity.
            status (str, kwargs): Optional case status.
            xid (str, kwargs): Optional case XID.

        Returns:
            CaseManagement.Case: A CM case object.
        """
        name = kwargs.get('name') or inspect.stack()[1].function
        artifacts = kwargs.get('artifacts', {})
        notes = kwargs.get('notes', [])
        severity = kwargs.get('case_severity') or 'Low'
        status = kwargs.get('case_status') or 'Open'
        tags = kwargs.get('tags', [])
        tasks = kwargs.get('tasks', {})
        xid = kwargs.get('xid') or f'xid-{inspect.stack()[1].function}'

        # create case
        case = self.cm.case(name=name, severity=severity, status=status, xid=xid)

        # add artifacts
        for artifact, artifact_data in artifacts.items():
            case.add_artifact(
                summary=artifact,
                intel_type=artifact_data.get('intel_type'),
                type=artifact_data.get('type'),
            )

        # add notes
        for note in notes:
            case.add_note(text=note)

        # add tags
        case.add_tag(name='pytest')
        for tag in tags:
            case.add_tag(name=tag)

        # add task
        for task, task_data in tasks.items():
            case.add_task(
                name=task, description=task_data.get('description'), status=task_data.get('status')
            )

        # submit task
        case.submit()

        # store case id for cleanup
        self.cases.append(case)

        return case

    def create_artifact(self, **kwargs):
        """Create an artifact (and optional case)

        If case_id is provided the ID will be used, otherwise a case_name will be dynamically
        created in the create_case method.

        Args:
            case_id (str, kwargs): Required case ID.
            intel_type: (str, kwargs): Required artifact intel type field.
            summary (str, kwargs): Required artifact summary.
            type (str, kwargs): Required artifact type.

        Returns:
            CaseManagement.Artifact: A CM artifact object.
        """
        # create the artifact data
        artifact_data = {
            'case_id': kwargs.get('case_id') or self.create_case().id,
            'intel_type': kwargs.get('intel_type') or 'indicator-ASN',
            'summary': kwargs.get('summary') or f'asn{randint(100,999)}',
            'type': kwargs.get('type') or 'ASN',
        }

        # create the artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        return artifact

    def create_note(self, **kwargs):
        """Create an note (and optional artifact, case, or task)

        Notes can be applied to 3 top level types: artifacts, cases, and tasks. This method expects
        that one ID for any of those types will be provided.

        Args:
            note_text (str, kwargs): Required note text.
            artifact_id (str, kwargs): Optional artifact ID.
            case_id (str, kwargs): Optional case ID.
            case_name (str, kwargs): Optional case name.
            case_xid (str, kwargs): Optional case XID.
            parent_type (str, kwargs): Optional parent type (artifact, case, task)
            task_id (str, kwargs): Optional artifact ID.

        Returns:
            CaseManagement.Artifact: A CM artifact object.
        """

        # create the note data dynamically
        note_data = {
            'date_added': kwargs.get('note_date_added'),
            'edited': kwargs.get('note_edited'),
            'last_modified': kwargs.get('note_last_modified'),
            'summary': kwargs.get('note_summary'),
            'text': kwargs.get('note_text'),
            'user_name': kwargs.get('note_user_name'),
        }

        # using provided data support parent type of artifact, case, or task.
        if kwargs.get('artifact_id'):
            note_data['artifact_id'] = kwargs.get('artifact_id')
        elif kwargs.get('case_id'):
            note_data['case_id'] = kwargs.get('case_id')
        elif kwargs.get('task_id'):
            note_data['task_id'] = kwargs.get('task_id')
        elif kwargs.get('parent_type'):
            parent_type = kwargs.pop('parent_type')
            if parent_type == 'artifact':
                artifact_data = {
                    'artifact_intel_type': 'indicator-ASN',
                    'artifact_summary': f'asn{randint(1000,9999)}',
                    'artifact_type': 'ASN',
                }
                artifact = self.create_artifact(**artifact_data)
                note_data['artifact_id'] = artifact.id
            elif parent_type == 'case':
                case = self.create_case()
                note_data['case_id'] = case.id
            elif parent_type == 'task':
                # task = self.create_task(**kwargs)
                # note_data['task_id'] = task.id
                pass

        # create the artifact
        note = self.cm.note(**note_data)
        note.submit()

        return note

    def create_task(self, **kwargs):
        """Create a task (and optional case)

        If case_id is provided the ID will be used, otherwise a case_name will be dynamically
        created in the create_case method.

        Args:
            task_name (str, kwargs): Required Task "Name" field.
            case_id (str, kwargs): Optional Case "ID".
            case_name (str, kwargs): Optional Case "Name".
            case_xid (str, kwargs): Optional Case "XID".
            task_description (str, kwargs): Optional Task "Description" field.
            task_is_workflow (bool, kwargs): Optional Task "Is Workflow" field.
            task_notes (dict, kwargs): Optional Task "Notes" field.
            task_source (str, kwargs): Optional Task "Source" field.
            task_status (str, kwargs): Optional Task "Status" field.
            task_workflow_id (int, kwargs): Optional Task "Workflow ID" field.
            task_workflow_phase (str, kwargs): Optional Task "Workflow Phase" field.
            task_workflow_step (str, kwargs): Optional Task "Workflow Step" field.
            task_xid (str, kwargs): Optional Task "XID" field.

        Returns:
            CaseManagement.Task: A CM task object.
        """
        # create the note data dynamically
        task_data = {
            'case_xid': kwargs.get('case_xid'),
            'description': kwargs.get('description'),
            'is_workflow': kwargs.get('is_workflow'),
            'name': kwargs.get('task_name'),
            # @bpurdy - what is notes suppposed to be?
            # 'notes': kwargs.get('task_notes', {}),
            'source': kwargs.get('task_source'),
            'status': kwargs.get('task_status'),
            'workflow_id': kwargs.get('task_workflow_id'),
            'workflow_phase': kwargs.get('task_workflow_phase'),
            'workflow_step': kwargs.get('task_workflow_step'),
        }

        if kwargs.get('case_id'):
            task_data['case_id'] = kwargs.get('case_id')
        else:
            # create a dummy case
            case = self.create_case(**kwargs)
            task_data['case_id'] = case.id

        # create the artifact
        task = self.cm.task(**task_data)
        task.submit()

        return task

    def cleanup(self):
        """Remove all cases and child data."""
        for case in self.cases:
            case.delete()

        # delete by tag

        # cases = self.cm.cases()
        # cases.filter.tag(TQL.Operator.EQ, 'pytest')
        # for case in cases:
        #     case.delete()

        # delete by name starts with

        # cases = self.cm.cases()
        # for case in cases:
        #     if case.name.startswith('tests.case_man'):
        #         case.delete(

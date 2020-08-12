# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
# standard library
import os
from datetime import datetime, timedelta
from random import randint

# first-party
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestNote(TestCaseManagement):
    """Test TcEx CM Note Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('note')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_note_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_note_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_note_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_note_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_note_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_note_create_by_case_id(self, request):
        """Test Note Creation on a Case."""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
            'date_added': '2033-12-07T14:16:40-05:00',
            'edited': True,
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # get single artifact by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    def test_note_create_by_artifact_id(self, request):
        """Test Note Get by Id"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # note data
        note_data = {
            'artifact_id': artifact.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # get single note by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    def test_note_create_by_artifact_id_property(self, request):
        """Test Note Get by Id"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # note data
        note_data = {
            'artifact_id': artifact.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note()
        note.artifact_id = note_data.get('artifact_id')
        note.text = note_data.get('text')
        note.submit()

        # get single note by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    def test_note_create_by_task_id(self, request):
        """Test Note Get by Id"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # note data
        note_data = {
            'task_id': task.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # get single note by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    def test_note_delete_by_id(self, request):
        """Test Note Deletion"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # get single artifact by id
        note = self.cm.note(id=note.id)

        # delete the note
        note.delete()

        # test note is deleted
        try:
            note.get()
            assert False
        except RuntimeError:
            pass

    def test_note_get_many_case(self):
        """Test Get Many Note Notes"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {__name__} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # iterate over all artifact looking for needle
        for a in self.cm.notes():
            if a.text == note_data.get('text'):
                break
        else:
            assert False

    def test_note_get_single_by_case_id(self):
        """Test Note Get by Id"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {__name__} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # get single note by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    def test_note_get_single_attached_to_artifact_by_id_properties(self, request):
        """Test Note on a Artifact"""
        case = self.cm_helper.create_case()

        file_data = (
            'RmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': 'pytest test file artifact',
            'type': 'Certificate File',
        }
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # note data
        note_data = {
            'artifact_id': artifact.id,
            'text': f'note_text - {request.node.name}',
        }

        # create not
        note = self.cm.note(**note_data)
        note.submit()

        # get note for asserts
        note = self.cm.note(id=note.id)
        note.get(all_available_fields=True)

        # get artifact for asserts
        artifact.get(all_available_fields=True)

        # run assertions on returned data
        assert note.artifact.id == artifact.id
        assert note.artifact_id == artifact.id

        assert len(artifact.notes) == 1
        for note in artifact.notes:
            assert note.summary == note_data.get('text')

    def test_note_get_single_attached_to_case_by_id_properties(self, request):
        """Test Note on a Case"""
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'case_xid': case.xid,
            'text': f'note_text - {request.node.name}',
        }

        # add properties
        note = self.cm.note(**note_data)
        note.case_id = note_data.get('case_id')
        note.case_xid = note_data.get('case_xid')
        note.text = note_data.get('text')

        # create note
        note.submit()

        # get note for asserts
        note = self.cm.note(id=note.id)
        note.get(all_available_fields=True)

        # TODO: @bpurdy - why is this getting added to the case twice
        # update (PUT) case with note
        # case.add_note(**note_data)
        # case.submit()

        # run assertions on returned data
        assert note.parent_case.id == case.id

        # make sure all objects were added
        assert len(case.notes) == 1
        for note in case.notes:
            assert note.summary == note_data.get('text')
        assert note.case_xid == case.xid

        # read-only
        assert note.author == os.getenv('API_ACCESS_ID')
        assert note.edited is False

        # test as_entity
        assert note.as_entity.get('id') == note.id

    def test_note_get_single_attached_to_task_by_id_properties(self, request):
        """Test Note on a Task"""
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'due_date': (datetime.now() + timedelta(days=2)).isoformat(),
            'name': f'name-{request.node.name}',
            'status': 'Open',
        }
        task = self.cm.task(**task_data)
        task.case_id = task_data.get('case_id')
        task.description = task_data.get('description')
        task.due_date = task_data.get('due_date')
        task.name = task_data.get('name')
        task.status = task_data.get('status')
        task.xid = request.node.name
        task.submit()

        # note data
        note_data = {
            'task_id': task.id,
            'task_xid': task.xid,
            'text': f'note_text - {request.node.name}',
        }
        note = self.cm.note()
        note.task_id = note_data.get('task_id')  # coverage: task_id setter
        note.task_xid = note_data.get('task_xid')  # coverage: task_id setter
        note.text = note_data.get('text')
        note.submit()

        # get note for asserts
        note = self.cm.note(id=note.id)
        note.get(all_available_fields=True)

        # get task for asserts
        task_id = task.id
        task = self.cm.task()
        task.id = task_id  # coverage: id setter
        task.get(all_available_fields=True)

        # run assertions on returned data
        assert note.task.id == task.id
        assert note.task_id == task.id
        assert note.task_xid == task.xid

        # run assertions on returned data
        assert len(task.notes) == 1
        for note in task.notes:
            assert note.summary == note_data.get('text')

    def test_note_get_single_attached_to_wf_event_by_id_properties(self, request):
        """Test Note on a Workflow Event"""
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': 'pytest test workflow event',
        }
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # note data
        note_data = {
            'workflow_event_id': workflow_event.id,
            'text': f'note_text - {request.node.name}',
        }
        note = self.cm.note()
        note.text = note_data.get('text')
        note.workflow_event_id = note_data.get('workflow_event_id')  # coverage: task_id setter
        note.submit()

        # get note for asserts
        note = self.cm.note(id=note.id)
        note.get(all_available_fields=True)

        # get wfe for asserts
        workflow_event_id = workflow_event.id
        workflow_event = self.cm.workflow_event(id=workflow_event.id)
        workflow_event.id = workflow_event_id  # coverage: id setter
        workflow_event.get(all_available_fields=True)

        # run assertions on returned data
        assert note.workflow_event.id == workflow_event.id
        # TODO: opened an issue with @mj to see why this field is not returned.
        assert note.workflow_event_id == workflow_event.id

        # run assertions on returned data
        assert len(workflow_event.notes) == 1
        for note in workflow_event.notes:
            assert note.summary == note_data.get('text')

    def test_note_get_by_tql_filter_artifact_id(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # note data
        note_data = {
            'artifact_id': artifact.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.artifact_id(TQL.Operator.EQ, artifact.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_author(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
            'date_added': '2033-12-07T14:16:40-05:00',
            'edited': True,
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.case_id(TQL.Operator.EQ, case.id)
        notes.filter.author(TQL.Operator.EQ, os.getenv('API_ACCESS_ID'))

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_case_id(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.case_id(TQL.Operator.EQ, case.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_date_added(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.case_id(TQL.Operator.EQ, case.id)
        notes.filter.date_added(
            TQL.Operator.GT, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_has_artifact(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # note data
        note_data = {
            'artifact_id': artifact.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.has_artifact.id(TQL.Operator.EQ, artifact.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_has_case(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.has_case.id(TQL.Operator.EQ, case.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_has_task(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # note data
        note_data = {
            'task_id': task.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.has_task.id(TQL.Operator.EQ, task.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_id(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.case_id(TQL.Operator.EQ, case.id)
        notes.filter.id(TQL.Operator.EQ, note.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_last_modified(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.case_id(TQL.Operator.EQ, case.id)
        notes.filter.last_modified(
            TQL.Operator.GT, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_summary(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # note data
        note_data = {
            'case_id': case.id,
            'summary': f'sample note for {request.node.name} test case.',
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.case_id(TQL.Operator.EQ, case.id)
        notes.filter.summary(TQL.Operator.EQ, note_data.get('summary'))

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_task_id(self, request):
        """Test Note Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # note data
        note_data = {
            'task_id': task.id,
            'text': f'sample note for {request.node.name} test case.',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.task_id(TQL.Operator.EQ, task.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_get_by_tql_filter_workflow_event_id(self, request):
        """Test Note Get by TQL"""
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': 'pytest test workflow event',
        }

        # create wfe
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # note data
        note_data = {
            'workflow_event_id': workflow_event.id,
            'text': f'note_text - {request.node.name}',
        }

        # create note
        note = self.cm.note(**note_data)
        note.submit()

        # retrieve note using TQL
        notes = self.cm.notes()
        notes.filter.workflow_event_id(TQL.Operator.EQ, workflow_event.id)

        for note in notes:
            assert note.text == note_data.get('text')
            break
        else:
            assert False, 'No notes returned for TQL'

    def test_note_create_entity(self, request):
        """Test Artifact Get by TQL"""
        # retrieve artifacts using TQL
        case = self.cm_helper.create_case()
        note_entity = {
            'type': 'Note',
            'case_id': case.id,
            'text': f'sample note for {request.node.name} test case.',
        }
        data = self.cm.create_entity(note_entity, os.getenv('API_DEFAULT_ORG'))
        assert data.get('text') == note_entity.get('text')

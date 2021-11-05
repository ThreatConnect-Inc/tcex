"""Test the TcEx API Module."""
# standard library
import os

# third-party
import time
import datetime
from random import randint

import pytest
from pytest import FixtureRequest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestCaseManagement, V3Helper


class TestNotes(TestCaseManagement):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('notes')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.v3_helper.cleanup()

    def test_note_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_note_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_note_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_note_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def _test_note_on_obj(self, request, cm_object):
        common_note_data = {
            'text': 'Generic Note Data. This is auto generated to ensure that adding a note '
                    'does not remove already existing notes.'
        }
        notes = self.v3.notes()

        # [Pre-Requisite] - Add a note to the provided cm object to ensure that it does not get
        # replaced/removed
        cm_object.add_note(**common_note_data)
        cm_object.submit()

        # [Pre-Requisite] - Add the note data to the appropriate object
        note_data = { 'text': f'sample note for {request.node.name} test.' }

        # [Pre-Requisite] - Add the appropriate filter for the notes object
        if cm_object.type_.lower() == 'artifact':
            notes.filter.artifact_id(TqlOperator.EQ, cm_object.model.id)
        elif cm_object.type_.lower() == 'case':
            notes.filter.case_id(TqlOperator.EQ, cm_object.model.id)
        elif cm_object.type_.lower() == 'task':
            notes.filter.task_id(TqlOperator.EQ, cm_object.model.id)
        elif cm_object.type_.lower() == 'workflow event':
            notes.filter.workflow_event_id(TqlOperator.EQ, cm_object.model.id)
        else:
            assert False, f'Invalid value {cm_object.type_} passed into _test_note_on_obj.'

        # [Create Testing] create the object
        note = self._add_note(cm_object, note_data, specify_type=True)

        note = self.v3.note(id=note.model.id)
        note.get()

        # [Retrieve Testing] validate the object returned is the same object
        assert note.model.text == note_data.get('text')

        # [Retrieve Testing] validate the object got added to the object
        assert len(notes) == 2
        for note in cm_object.notes:
            if note.model.text == note_data.get('text'):
                break
        else:
            assert False, f'No note found -> {note.model.id}'

        # [Update Testing] validate the object got updated
        note.model.text = 'updated note value'
        note.submit()
        assert len(notes) == 2
        for note in cm_object.notes:
            if note.model.text == 'updated note value':
                break
        else:
            assert False, f'Note on {cm_object.type_} not updated -> {note.model.id}'

        note.delete()
        # [Delete Testing] validate the object got deleted to the object
        assert len(notes) == 1
        for remaining_note in cm_object.notes:
            if remaining_note.model.id == note.model.id:
                assert False, (
                    f'Note found on {cm_object.type_} when it should not have been present.'
                )
        # [Delete Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            note.get()

        # [Delete Testing] assert error message contains the correct code
        # error -> "(952, 'Error during GET. API status code: 404, ..."
        assert '952' in str(exc_info.value)

    def test_note_on_case(self, request: FixtureRequest):
        """Test Note functions on a Case Object"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()
        self._test_note_on_obj(request, case)

    def test_note_on_artifact(self, request: FixtureRequest):
        """Test Note functions on a Artifact Object"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create artifact
        artifact_data = {
            'case_id': case.model.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        artifact = self.v3.task(**artifact_data)
        self._test_note_on_obj(request, artifact)

    def test_note_on_task(self, request: FixtureRequest):
        """Test Note functions on a Task Object"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create task
        task_data = {
            'case_id': case.model.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        task = self.v3.task(**task_data)
        self._test_note_on_obj(request, task)

    def test_note_on_workflow_event(self, request: FixtureRequest):
        """Test Note functions on a Workflow Event Object"""

        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create task
        workflow_event_data = {
            'case_id': case.model.id,
            'summary': 'pytest test workflow event',
        }

        workflow_event = self.v3.workflow_event(**workflow_event_data)

        self._test_note_on_obj(request, workflow_event)

    def test_note_get_many(self):
        """Test Artifact Get Many"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()
        note_count = 10
        note_ids = []
        for _ in range(0, note_count):
            # [Create Testing] define object data
            note_data = {
                'case_id': case.model.id,
                'text': f'sample note randomint - {randint(100, 999)}'
            }

            # [Create Testing] create the object
            note = self.v3.note(**note_data)

            # [Create Testing] submit the object to the TC API
            note.submit()
            note_ids.append(note.model.id)

        # [Retrieve Testing] iterate over all object looking for needle
        notes = self.v3.notes(params={'resultLimit': 5})
        notes.filter.case_id(TqlOperator.EQ, case.model.id)
        assert len(notes) == note_count
        for note in notes:
            assert note.model.id in note_ids
            note_ids.remove(note.model.id)

        assert not note_ids, 'Not all artifacts were returned.'

    def test_note_get_by_tql_filter_fail_tql(self):
        """Test Artifact Get by TQL"""
        # retrieve object using TQL
        notes = self.v3.notes()
        notes.filter.tql = 'Invalid TQL'

        # [Fail Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            for _ in notes:
                pass

        # [Fail Testing] assert error message contains the correct code
        # error -> "(950, 'Error during pagination. API status code: 400, ..."
        assert '950' in str(exc_info.value)
        assert notes.request.status_code == 400

    def _add_note(self, cm_object, note_data, specify_type=False):
        """Update the note_data object to include either the artifact/case/task/or workflow_event field."""

        keys = ['artifact_id', 'case_id', 'task_id', 'workflow_event_id']
        for key in keys:
            if key in note_data:
                note_data.pop(key)
        if specify_type:
            note_data['text'] = note_data['text'] + f'Type -> {cm_object.type_}'

        if cm_object.type_.lower() == 'artifact':
            note_data['artifact_id'] = cm_object.model.id
        elif cm_object.type_.lower() == 'case':
            note_data['case_id'] = cm_object.model.id
        elif cm_object.type_.lower() == 'task':
            note_data['task_id'] = cm_object.model.id
        elif cm_object.type_.lower() == 'workflow event':
            note_data['workflow_event_id'] = cm_object.model.id
        else:
            assert False, f'Invalid value {cm_object.type_} passed into _test_note_on_obj'
        note = self.v3.note(**note_data)
        note.submit()
        return note

    def test_note_all_filters(self, request: FixtureRequest):
        """Test TQL Filters for Notes"""
        # [Pre-Requisite] - create case
        note_data = {'text': f'sample note for {request.node.name} test.'}
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create workflow_event
        workflow_event_data = {
            'case_id': case.model.id,
            'summary': 'pytest test workflow event',
        }

        workflow_event = self.v3.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # [Pre-Requisite] - create task
        task_data = {
            'case_id': case.model.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        task = self.v3.task(**task_data)
        task.submit()

        # [Pre-Requisite] - create artifact
        artifact_data = {
            'case_id': case.model.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        artifact = self.v3.artifact(**artifact_data)
        artifact.submit()

        note = self._add_note(case, note_data, specify_type=True)

        notes = self.v3.notes()

        future = datetime.datetime.now() + datetime.timedelta(days=10)
        future = future.strftime('%Y-%m-%dT%H:%M:%S')
        past = datetime.datetime.now() + datetime.timedelta(days=-10)
        past = past.strftime('%Y-%m-%dT%H:%M:%S')
        # [Filter Testing] case_id
        notes.filter.case_id(TqlOperator.EQ, case.model.id)
        # [Filter Testing] author
        notes.filter.author(TqlOperator.NE, 'Random User')
        # [Filter Testing] date_added
        notes.filter.date_added(TqlOperator.GT, past)
        # [Filter Testing] has_case -> using id since it's available
        notes.filter.has_case.id(TqlOperator.EQ, case.model.id)
        # [Filter Testing] id
        notes.filter.id(TqlOperator.EQ, note.model.id)
        # [Filter Testing] last_modified
        notes.filter.last_modified(TqlOperator.LT, future)
        # [Filter Testing] summary
        notes.filter.summary(TqlOperator.NE, 'Invalid Summary')

        # TODO: It does not appear that NE operator works as expected
        for retrieved_note in notes:
            assert retrieved_note.model.text == note.model.text
            break
        else:
            assert False, f'No note found for tql -> {notes.tql.as_str}'

        notes = self.v3.notes()
        note = self._add_note(artifact, note_data, specify_type=True)

        notes.filter.artifact_id(TqlOperator.EQ, artifact.model.id)
        notes.filter.has_artifact.id(TqlOperator.EQ, artifact.model.id)

        for retrieved_note in notes:
            assert retrieved_note.model.text == note.model.text
            break
        else:
            assert False, f'No note found for tql -> {notes.tql.as_str}'

        notes = self.v3.notes()
        note = self._add_note(task, note_data, specify_type=True)

        notes.filter.task_id(TqlOperator.EQ, task.model.id)
        notes.filter.has_task.id(TqlOperator.EQ, task.model.id)

        assert len(notes) == 1, f'Invalid amount of notes retried for tql -> {notes.tql.as_str}'
        for retrieved_note in notes:
            assert retrieved_note.model.text == note.model.text
            break
        else:
            assert False, f'No note found for tql -> {notes.tql.as_str}'

        notes = self.v3.notes()
        note = self._add_note(workflow_event, note_data, specify_type=True)

        notes.filter.workflow_event_id(TqlOperator.EQ, workflow_event.model.id)
        for retrieved_note in notes:
            assert retrieved_note.model.text == note.model.text
            break
        else:
            assert False, f'No note found for tql -> {notes.tql.as_str}'

# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
from datetime import datetime, timedelta
from random import randint
from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


# pylint: disable=W0201
class TestNoteIndicators:
    """Test TcEx CM Note Interface."""

    cm = None
    cm_helper = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper(self.cm)

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

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
            'last_modified': '',
            'summary': '',
            'user_name': '',
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
            'last_modified': '',
            'summary': '',
            'user_name': '',
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

    # TODO: update this
    def test_note_get_by_tql_filter_workflow_event_id(self):
        """Test Note Get by TQL"""

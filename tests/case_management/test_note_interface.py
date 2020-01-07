# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os

# from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


# pylint: disable=W0201
class TestNoteIndicators:
    """Test TcEx CM Note Inteface."""

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

    def test_create_by_case_id(self):
        """Test Note Creation on a Case."""

        # create case
        case = self.cm_helper.create_case(case_name=__name__)

        note_data = {
            'text': f'sample note for {__name__} test case.',
        }

        # create note
        note = self.cm.note(
            case_id=case.id,
            # date_added=note_data.get('date_added'),
            # edited=note_data.get('edited'),
            # last_modified=note_data.get('last_modified'),
            # summary=note_data.get('summary'),
            text=note_data.get('text'),
            # user_name=note_data.get('user_name'),
        )
        note.submit()

        # get single artifact by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    def test_get_single_by_artifact_id(self):
        """Test Note Get by Id"""
        note_data = {
            'parent_type': 'artifact',
            'text': f'sample note for {__name__} test case.',
        }

        # create artifact
        note = self.cm_helper.create_note(**note_data)

        # get single note by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    def test_get_many_artifact_notes(self):
        """Test Get Many Artifact Notes"""
        note_data = {
            'parent_type': 'artifact',
            'text': f'sample note for {__name__} test case.',
        }

        # create artifact
        self.cm_helper.create_note(**note_data)

        # iterate over all artifact looking for needle
        for a in self.cm.notes():
            if a.text == note_data.get('text'):
                break
        else:
            assert False

    def test_get_many_case_notes(self):
        """Test Get Many Case Notes"""
        note_data = {
            'parent_type': 'case',
            'text': f'sample note for {__name__} test case.',
        }

        # create artifact
        self.cm_helper.create_note(**note_data)

        # iterate over all artifact looking for needle
        for a in self.cm.notes():
            if a.text == note_data.get('text'):
                break
        else:
            assert False

    def test_get_single_by_case_id(self):
        """Test Note Get by Id"""
        note_data = {
            'parent_type': 'case',
            'text': f'sample note for {__name__} test case.',
        }

        # create artifact
        note = self.cm_helper.create_note(**note_data)

        # get single note by id
        note = self.cm.note(id=note.id)
        note.get()

        # run assertions on returned data
        assert note.text == note_data.get('text')

    # def test_tql(self):

    # def test_delete(self, name='tag_name', create=True):
    #     """[summary]

    #     Args:
    #         name (str, optional): [description]. Defaults to 'tag_name'.
    #         create (bool, optional): [description]. Defaults to True.
    #     """
    #     if create:
    #         self.test_create(name, delete=False)
    #     tags = self.cm.tags()
    #     tags.name_filter(TQL.Operator.EQ, name)
    #     for tag in tags:
    #         tag.delete()

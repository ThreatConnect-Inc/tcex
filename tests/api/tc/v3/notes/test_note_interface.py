"""Test the TcEx API Module."""
# standard library
import os

# third-party
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

    def test_note_create_on_case(self, request: FixtureRequest):
        """Test Note Creation on a Case."""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define object data
        note_data = {
            'case_id': case.model.id,
            'text': f'sample note for {request.node.name} test case.',
            'date_added': '2033-12-07T14:16:40-05:00',
            'edited': True,
        }

        # [Create Testing] create the object
        note = self.v3.note(**note_data)

        # [Create Testing] submit the object to the TC API
        note.submit()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        note = self.v3.note(id=note.model.id)
        note.get()

        # run assertions on returned data
        assert note.model.text == note_data.get('text')

    def test_note_get_many(self):
        """Test Artifact Get Many"""
        # [Retrieve Testing] iterate over all object looking for needle
        notes = self.v3.notes()
        for note in notes:
            if note.model.name == 'Protocol Number':
                assert note._api_endpoint == '/v3/notes'
                assert note.model.data_type == 'String'
                assert note.model.description.startswith('In the Internet Protocol')
                break
        else:
            assert False, 'Artifact type of "Protocol Number" was not returned.'

    def test_note_get_single_by_id_properties(self):
        """Test Artifact get single attached to task by id"""

        # [Create Testing] Istanciate a instance of the Artifact Type
        note = self.v3.note()

        # [Create Testing] testing setters on model
        note.model.id = 1

        # [Retrieve Testing] get the object from the API
        note.get()

        # [Retrieve Testing] run assertions on returned data
        assert note.model.id == 1
        assert note.model.name == 'Email Address'
        assert note.model.description.startswith('A name that identifies')
        assert note.model.data_type == 'String'
        assert note.model.intel_type == 'indicator-EmailAddress'

        assert note.as_entity == {
            'type': 'ArtifactType', 'id': 1, 'value': 'Email Address'
        }

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

    def test_note_all_filters(self):
        """Test TQL Filters for artifact on a Case"""

        notes = self.v3.notes()

        # [Filter Testing] active
        notes.filter.active(TqlOperator.EQ, True)

        # [Filter Testing] data type
        notes.filter.data_type(TqlOperator.EQ, 'String')

        # [Filter Testing] description
        notes.filter.description(
            TqlOperator.EQ,
            'A name that identifies an electronic post office box on '
            'a network where Electronic-Mail (e-mail) can be sent.',
        )

        # [Filter Testing] id
        notes.filter.id(TqlOperator.EQ, 1)

        # [Filter Testing] intel type
        notes.filter.intel_type(TqlOperator.EQ, 'indicator-EmailAddress')

        # [Filter Testing] managed
        notes.filter.managed(TqlOperator.EQ, True)

        # [Filter Testing] name
        notes.filter.name(TqlOperator.EQ, 'Email Address')

        for note in notes:
            assert note.model.id == 1
            assert note.model.name == 'Email Address'
            assert note.model.description.startswith('A name that identifies')
            assert note.model.data_type == 'String'
            assert note.model.intel_type == 'indicator-EmailAddress'
            break
        else:
            assert False, f'No artifact found for tql -> {notes.tql.as_str}'
        assert len(notes) == 1, ('More than 1 artifact type retrieved for tql '
                                          f'{notes.tql.as_str}.')

"""TcEx Framework Module"""

import pytest

from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestExclusionLists(TestV3):
    """Test TcEx API Interface."""
    v3_helper = V3Helper('exclusion_lists')

    def test_exclusion_list_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_exclusion_list_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_exclusion_list_object_properties(self):
        """Test properties."""
        super().obj_properties()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_exclusion_list_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_exclusion_list_get_all(self):
        """Test retrieving all exclusion_lists."""
        exclusion_lists_exists = False
        for _ in self.tcex.api.tc.v3.exclusion_lists():
            exclusion_lists_exists = True
            break
        assert exclusion_lists_exists, 'No exclusion_lists found.'

    def test_exclusion_list_get_by_id(self):
        """Test retrieving a single exclusion_list by id."""
        exclusion_list = self.tcex.api.tc.v3.exclusion_list(id=1)
        exclusion_lists_exists = False
        for exclusion_list in self.tcex.api.tc.v3.exclusion_lists():
            id_ = exclusion_list.model.id
            retrieved_exclusion_list = self.tcex.api.tc.v3.exclusion_list(id=id_)
            retrieved_exclusion_list.get()
            assert retrieved_exclusion_list.model.id == id_
            return
        assert exclusion_lists_exists, 'No exclusion_lists found.'

    def test_exclusion_list_create(self):
        """Test creating a new exclusion_list."""
        name = None
        for exclusion_list in self.tcex.api.tc.v3.exclusion_lists():
            name = exclusion_list.model.name
            break
        assert name is not None, 'No exclusion_lists found.'
        details = {
            'name': name,
            'fixedValues': {'mode': 'replace', 'data': [{'value': 'fixedvalue'}]},
            'variableValues': {'mode': 'replace', 'data': [{'value': 'variablevalue'}]},
            'owner': 'TCI',
            'ownerId': 3,
        }
        exclusion_list = self.tcex.api.tc.v3.exclusion_list(**details)
        exclusion_list.create()
        try:
            assert exclusion_list.model.id is not None, 'Exclusion List was not created.'
        finally:
            exclusion_list.delete()

    def test_exclusion_list_tql(self):
        """Test Artifact get single attached to task by id"""
        # [Create testing] create a temporary exclusion_list
        name = None
        for exclusion_list in self.tcex.api.tc.v3.exclusion_lists():
            name = exclusion_list.model.name
            break
        assert name is not None, 'No exclusion_lists found.'
        details = {
            'name': name,
            'fixedValues': {'mode': 'replace', 'data': [{'value': 'fixedvalue'}]},
            'variableValues': {'mode': 'replace', 'data': [{'value': 'variablevalue'}]},
            'owner': 'TCI',
            'ownerId': 3,
        }
        new_exclusion_list = self.tcex.api.tc.v3.exclusion_list(**details)
        new_exclusion_list.create()
        exclusion_lists = self.v3.exclusion_lists()
        exclusion_lists.filter.name(TqlOperator.EQ, name)
        exclusion_lists.filter.id(TqlOperator.EQ, new_exclusion_list.model.id)
        exclusion_lists.filter.owner(TqlOperator.EQ, new_exclusion_list.model.owner_id)
        exclusion_lists.filter.managed(TqlOperator.EQ, False)
        exclusion_lists.filter.active(TqlOperator.EQ, True)
        # [Create Testing] testing setters on model
        try:
            exclusion_list = None
            counter = 0
            for exclusion_list in exclusion_lists:
                counter += 1
            assert counter == 1, 'Exclusion List was not created.'
            assert exclusion_list.model.id == new_exclusion_list.model.id
            assert exclusion_list.model.name == new_exclusion_list.model.name
            assert exclusion_list.model.owner == new_exclusion_list.model.owner
            assert exclusion_list.model.managed is new_exclusion_list.model.managed
            assert exclusion_list.model.active is new_exclusion_list.model.active
        finally:
            new_exclusion_list.delete()

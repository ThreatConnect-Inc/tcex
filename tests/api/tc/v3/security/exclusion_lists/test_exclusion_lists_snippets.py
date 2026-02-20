"""TcEx Framework Module"""

from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestExclusionListSnippets(TestV3):
    """Test TcEx API Interface."""
    v3_helper = V3Helper('exclusion_lists')
    def test_exclusion_list_get_all(self):
        """Test snippet"""
        # Begin Snippet
        for exclusion_list in self.tcex.api.tc.v3.exclusion_lists():
            print(exclusion_list.model.dict(exclude_none=True))
        # End Snippet
    def test_exclusion_list_tql_filter(self):
        """Test snippet"""
        # Begin Snippet
        exclusion_lists = self.tcex.api.tc.v3.exclusion_lists()
        exclusion_lists.filter.name(TqlOperator.EQ, 'temp_exclusion_list')
        for exclusion_list in exclusion_lists:
            print(exclusion_list.model.dict(exclude_none=True))
        # End Snippet
    def test_exclusion_list_get_by_id(self):
        """Test snippet"""
        # Begin Snippet
        exclusion_list = self.tcex.api.tc.v3.exclusion_list(id=1)
        exclusion_list.get()
        print(exclusion_list.model.dict(exclude_none=True))
        # End Snippet

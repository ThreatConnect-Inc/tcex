"""Test the TcEx API Snippets."""
# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestAttributeTypeSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('attribute_types')

    def test_attribute_types_get_all(self):
        """Test snippet"""
        # Begin Snippet
        for attribute_type in self.tcex.api.tc.v3.attribute_types():
            print(attribute_type.model.dict(exclude_none=True))
        # End Snippet

    def test_attribute_types_tql_filter(self):
        """Test snippet"""
        # Begin Snippet
        attribute_types = self.tcex.api.tc.v3.attribute_types(params={'fields': ['mapping']})
        attribute_types.filter.associated_type(TqlOperator.EQ, 'Adversary')
        attribute_types.filter.system(TqlOperator.EQ, True)
        for attribute_type in attribute_types:
            print(attribute_type.model.dict(exclude_none=True))
        # End Snippet

    def test_attribute_type_get_by_id(self):
        """Test snippet"""
        # Begin Snippet
        attribute_type = self.tcex.api.tc.v3.attribute_type(id=1)
        attribute_type.get()
        print(attribute_type.model.dict(exclude_none=True))
        # End Snippet

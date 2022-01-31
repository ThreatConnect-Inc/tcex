"""Test the TcEx API Snippets."""
# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


@pytest.mark.xdist_group(name='victim-attribute-snippets')
class TestVictimAttributeSnippets(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self, method: callable):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('victim_attributes')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # remove an previous indicators with the next test case name as a tag
        victims = self.v3.victims()
        victims.filter.tag(TqlOperator.EQ, method.__name__)
        for victim in victims:
            victim.delete()

    # TODO [PLAT-4144] - next url is invalid
    # def test_victim_attributes_get_all(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     for victim_attribute in self.tcex.v3.victim_attributes():
    #         print(victim_attribute.model.dict(exclude_none=True))
    #     # End Snippet

    def test_victim_attributes_tql_filter(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
        )
        # get attribute id
        attribute_id = victim.model.attributes.data[0].id

        # Begin Snippet
        victim_attributes = self.tcex.v3.victim_attributes()
        victim_attributes.filter.date_added(TqlOperator.GT, '1 day ago')
        victim_attributes.filter.displayed(TqlOperator.EQ, True)
        victim_attributes.filter.id(TqlOperator.EQ, attribute_id)
        victim_attributes.filter.victim_id(TqlOperator.EQ, victim.model.id)
        victim_attributes.filter.last_modified(TqlOperator.GT, '1 day ago')
        victim_attributes.filter.type_name(TqlOperator.EQ, 'Description')
        for victim_attribute in victim_attributes:
            print(victim_attribute.model.dict(exclude_none=True))
        # End Snippet

    def test_victim_attribute_get_by_id(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
        )
        # get attribute id
        attribute_id = victim.model.attributes.data[0].id

        # Begin Snippet
        victim_attribute = self.tcex.v3.victim_attribute(id=attribute_id)
        victim_attribute.get()
        print(victim_attribute.model.dict(exclude_none=True))
        # End Snippet

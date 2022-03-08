"""Test the TcEx API Snippets."""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper

if TYPE_CHECKING:
    # third-party
    from pytest import FixtureRequest


class TestIndicatorAttributeSnippets(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self, method: callable):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('indicator_attributes')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # remove an previous indicators with the next test case name as a tag
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, method.__name__)
        for indicator in indicators:
            indicator.delete()

    # TODO: an issue in core is preventing this test from working
    # def test_indicator_attributes_get_all(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     for indicator_attribute in self.tcex.v3.indicator_attributes():
    #         print(indicator_attribute.model.dict(exclude_none=True))
    #     # End Snippet

    def test_indicator_attributes_tql_filter(self, request: 'FixtureRequest'):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            value1='111.111.111.200',
            type='Address',
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
            tags=[{'name': request.node.name}],
        )
        # get attribute id
        attribute_id = indicator.model.attributes.data[0].id

        # Begin Snippet
        indicator_attributes = self.tcex.v3.indicator_attributes()
        indicator_attributes.filter.date_added(TqlOperator.GT, '1 day ago')
        indicator_attributes.filter.displayed(TqlOperator.EQ, True)
        indicator_attributes.filter.id(TqlOperator.EQ, attribute_id)
        indicator_attributes.filter.indicator_id(TqlOperator.EQ, indicator.model.id)
        indicator_attributes.filter.last_modified(TqlOperator.GT, '1 day ago')
        indicator_attributes.filter.type_name(TqlOperator.EQ, 'Description')
        for indicator_attribute in indicator_attributes:
            print(indicator_attribute.model.dict(exclude_none=True))
        # End Snippet

    def test_indicator_attribute_get_by_id(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            value1='111.111.111.202',
            type='Address',
            attributes=[
                {
                    'default': True,
                    'type': 'Description',
                    'value': 'An example description attribute',
                }
            ],
        )
        # get attribute id
        attribute_id = indicator.model.attributes.data[0].id

        # Begin Snippet
        indicator_attribute = self.tcex.v3.indicator_attribute(id=attribute_id)
        indicator_attribute.get()
        print(indicator_attribute.model.dict(exclude_none=True))
        # End Snippet

"""Test the TcEx API Snippets."""
# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestIndicatorAttributeSnippets(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('indicator_attributes')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    # TODO [PLAT-4144] - next url is invalid
    # def test_indicator_attributes_get_all(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     for indicator_attribute in self.tcex.v3.indicator_attributes():
    #         print(indicator_attribute.model.dict(exclude_none=True))
    #     # End Snippet

    def test_indicator_attributes_tql_filter(self):
        """Test snippet"""
        indicator = self.v3_helper.create_indicator(
            value1='111.111.111.111',
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
            value1='111.111.111.111',
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

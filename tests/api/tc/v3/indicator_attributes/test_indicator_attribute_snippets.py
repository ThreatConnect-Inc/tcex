"""TcEx Framework Module"""
# standard library
from collections.abc import Callable

# third-party
from _pytest.fixtures import FixtureRequest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestIndicatorAttributeSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('indicator_attributes')

    def setup_method(self, method: Callable):  # pylint: disable=arguments-differ
        """Configure setup before all tests."""
        super().setup_method()

        # remove an previous indicators with the next test case name as a tag
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, method.__name__)
        for indicator in indicators:
            indicator.delete()

    # TODO: an issue in core is preventing this test from working
    # def test_indicator_attributes_get_all(self):
    #     """Test snippet"""
    #     # Begin Snippet
    #     for indicator_attribute in self.tcex.api.tc.v3.indicator_attributes():
    #         print(indicator_attribute.model.dict(exclude_none=True))
    #     # End Snippet

    def test_indicator_attributes_tql_filter(self, request: FixtureRequest):
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
        assert indicator.model.attributes.data is not None, 'No attributes found.'
        attribute_id = indicator.model.attributes.data[0].id
        assert attribute_id is not None, 'No attribute id found.'
        indicator_id = indicator.model.id
        assert indicator_id is not None, 'No indicator id found.'

        # Begin Snippet
        indicator_attributes = self.tcex.api.tc.v3.indicator_attributes()
        indicator_attributes.filter.date_added(TqlOperator.GT, '1 day ago')
        indicator_attributes.filter.displayed(TqlOperator.EQ, True)
        indicator_attributes.filter.id(TqlOperator.EQ, attribute_id)
        indicator_attributes.filter.indicator_id(TqlOperator.EQ, indicator_id)
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
        assert indicator.model.attributes.data is not None, 'No attributes found.'
        attribute_id = indicator.model.attributes.data[0].id

        # Begin Snippet
        indicator_attribute = self.tcex.api.tc.v3.indicator_attribute(id=attribute_id)
        indicator_attribute.get()
        print(indicator_attribute.model.dict(exclude_none=True))
        # End Snippet

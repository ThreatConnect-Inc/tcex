"""Test the TcEx API Module."""
# standard library
import os
import time
from datetime import datetime, timedelta
from random import randint

# third-party
from pytest import FixtureRequest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestCaseManagement, V3Helper


class TestIndicators(TestCaseManagement):
    """Test TcEx API Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('indicators')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        # TODO: [med] @bpurdy - do you recall what the condition is for?
        if os.getenv('TEARDOWN_METHOD') is None:
            self.v3_helper.cleanup()

    def test_indicator_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_indicator_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_indicator_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_indicator_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    # def test_return_indicators(self, request: FixtureRequest):
    #     """Test Object Creation

    #     A single test case to hit all sub-type creation (e.g., Notes).
    #     """
    #     indicators = self.v3_helper.v3_obj_collection
    #     indicators = self.v3.indicators(params={'fields': 'securityLabels'})
    #     indicators.filter.summary(TqlOperator.EQ, '123.123.123.123')
    #     for indicator in indicators:
    #         indicator.get(params={'fields': ['_all_']})
    #         print(indicator.model.json(indent=4, exclude_none=True))

    #     return

    def test_indicator_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        # [Create Testing] define object data
        indicator_data = {
            'active': True,
            'confidence': 75,
            'description': 'TcEx Testing',
            'ip': '123.123.123.124',
            'rating': 3,
            'source': None,
            'type': 'Address',
        }
        indicator = self.v3.indicator(**indicator_data)

        # [Create Testing] define object data
        attribute_data = {
            'type': 'Description',
            'value': 'TcEx Testing',
            'default': True,
        }
        indicator.add_attribute(**attribute_data)

        # [Create Testing] define object data
        security_label_data = {
            'name': 'TLP:WHITE',
        }
        indicator.add_security_label(**security_label_data)

        # [Create Testing] define object data
        tag_data = {
            'name': 'TcEx Testing',
        }
        indicator.add_tag(**tag_data)

        # print(indicator.model.dict())
        indicator.submit()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        self.v3.indicator(id=indicator.model.id)

        # [Retrieve Testing] get the object from the API
        indicator.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        indicator.model.summary == indicator_data.get('ip')
        indicator.model.ip == indicator_data.get('ip')

        # [Retrieve Testing] run assertions on returned nested data
        indicator.model.attributes.data[0].value == attribute_data.get('value')

        # [Retrieve Testing] run assertions on returned nested data
        indicator.model.security_labels.data[0].name == security_label_data.get('name')

        # [Retrieve Testing] run assertions on returned nested data
        indicator.model.tags.data[0].name == tag_data.get('name')

        # print('status_code', indicator.request.status_code)
        # print('method', indicator.request.request.method)
        # print('url', indicator.request.request.url)
        # print('body', indicator.request.request.body)
        # print('text', indicator.request.text)

    def test_indicator_get_many(self):
        """Test Indicators Get Many"""
        # # [Pre-Cleanup] - create case (requires v3ApiBulkDeleteAllowed to be enabled)
        # indicators = self.v3.indicators()
        # indicators.filter.tag(TqlOperator.EQ, indicator_tag)
        # indicators.delete()

        # [Pre-Requisite] - create case
        indicator_count = 10
        indicator_ids = []
        indicator_tag = 'TcEx-Indicator-Testing'
        for i in range(0, indicator_count):
            # [Create Testing] define object data
            indicator_data = {
                'active': True,
                'confidence': 75,
                'description': 'TcEx Testing',
                'ip': f'123.123.125.{i}',
                'rating': 3,
                'source': None,
                'tags': {'data': [{'name': indicator_tag}]},
                'type': 'Address',
            }
            indicator = self.v3.indicator(**indicator_data)
            indicator.submit()
            indicator_ids.append(indicator.model.id)
            self.v3_helper._v3_objects.append(indicator)

        # [Retrieve Testing] iterate over all object looking for needle
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, indicator_tag)
        # capture indicator count before deleting the indicator
        indicators_counts = len(indicators)
        for i, indicator in enumerate(indicators):
            assert indicator.model.id in indicator_ids
            indicator_ids.remove(indicator.model.id)

            # cleanup the indicator
            # indicator.delete()

        assert indicators_counts == indicator_count
        assert not indicator_ids, 'Not all indicators were returned.'

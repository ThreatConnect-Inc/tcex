"""Test the TcEx API Module."""
# standard library
import os
import time
from datetime import datetime, timedelta
from random import randint

# third-party
import pytest
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
        self.ti = self.v3_helper.ti
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

    def test_indicator_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        indicators = self.v3_helper.v3_obj_collection
        indicators.filter.summary(TqlOperator.EQ, '123.123.123.123')
        for indicator in indicators:
            indicator.model.rating = 3
            indicator.submit()
            # print(indicator.blah.writable)
            # print(indicator.model.json(indent=4))
            # print(indicator.post_properties)
            indicator.get(all_available_fields=True)
            # print(indicator.model.json(exclude_none=True, indent=2))
            print('writable', indicator.results.writable)
            # print('raw', indicator.results.raw)

        # [Create Testing] define object data
        object_data = {
            'active': True,
            'attributes': {
                'data': [
                    {
                        'type': 'Description',
                        'value': 'TcEx Testing',
                        'default': True,
                    }
                ]
            },
            'confidence': 75,
            'description': 'TcEx Testing',
            'ip': '123.123.123.124',
            'rating': 3,
            'source': None,
            'tags': {
                'data': [
                    {
                        'name': 'TcEx Testing',
                    }
                ]
            },
            'type': 'Address',
            # 'xid': '123.123.123.124',
        }
        indicator = self.ti.indicator(**object_data)
        print(indicator.model.dict())
        try:
            indicator.submit()
        except RuntimeError:
            pass
        print('status_code', indicator.request.status_code)
        print('method', indicator.request.request.method)
        print('url', indicator.request.request.url)
        print('body', indicator.request.request.body)
        print('text', indicator.request.text)

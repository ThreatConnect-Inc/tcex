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


class TestGroups(TestCaseManagement):
    """Test TcEx API Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('groups')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        # TODO: [med] @bpurdy - do you recall what the condition is for?
        if os.getenv('TEARDOWN_METHOD') is None:
            self.v3_helper.cleanup()

    def test_group_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_group_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_group_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_group_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_group_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        groups = self.v3_helper.v3_obj_collection
        # groups.filter.summary(TqlOperator.EQ, '123.123.123.123')
        for group in groups:
            # print(group.blah.writable)
            # print(group.model.json(indent=4))
            # print(group.post_properties)
            group.get(all_available_fields=True)
            # print(group.model.json(exclude_none=True, indent=2))
            print('writable', group.results.writable)
            # print('raw', group.results.raw)

        # # [Create Testing] define object data
        # object_data = {
        #     'active': True,
        #     'attributes': {
        #         'data': [
        #             {
        #                 'type': 'Description',
        #                 'value': 'TcEx Testing',
        #                 'default': True,
        #             }
        #         ]
        #     },
        #     'confidence': 75,
        #     'description': 'TcEx Testing',
        #     'ip': '123.123.123.124',
        #     'rating': 3,
        #     'source': None,
        #     'tags': {
        #         'data': [
        #             {
        #                 'name': 'TcEx Testing',
        #             }
        #         ]
        #     },
        #     'type': 'Address',
        #     # 'xid': '123.123.123.124',
        # }
        # group = self.v3.group(**object_data)
        # print(group.model.dict())
        # try:
        #     group.submit()
        # except RuntimeError:
        #     pass
        # print('status_code', group.request.status_code)
        # print('method', group.request.request.method)
        # print('url', group.request.request.url)
        # print('body', group.request.request.body)
        # print('text', group.request.text)

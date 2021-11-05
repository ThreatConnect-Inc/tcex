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

    def test_indicator_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        indicators = self.v3_helper.v3_obj_collection
        indicators = self.v3.indicators(params={'fields': 'securityLabels'})
        indicators.filter.summary(TqlOperator.EQ, '123.123.123.123')
        for indicator in indicators:
            indicator.get('all_available_fields')
            print(indicator.model.json(indent=4, exclude_none=True))

        return

        """
        "associatedGroups": {
                "data": [
                    {
                        "id": 30612,
                        "type": "Adversary",
                        "ownerName": "TCI",
                        "dateAdded": "2021-11-05T13:44:43Z",
                        "webLink": "/auth/adversary/adversary.xhtml?adversary=30612",
                        "name": "adversary-001",
                        "createdBy": "Bracey Summers"
                    }
                ],
                "count": 1
            },
            "associatedIndicators": {
                "data": [
                    {
                        "id": 62620,
                        "type": "Address",
                        "ownerName": "TCI",
                        "dateAdded": "2021-11-03T23:54:08Z",
                        "webLink": "/auth/indicators/details/address.xhtml?address=123.123.123.123",
                        "lastModified": "2021-11-04T17:15:31Z",
                        "rating": 3.00,
                        "confidence": 75,
                        "description": "TcEx Testing",
                        "summary": "123.123.123.123",
                        "privateFlag": false,
                        "active": true,
                        "activeLocked": false,
                        "ip": "123.123.123.123"
                    }
                ],
                "count": 1
            },
            "ip": "123.123.123.124"
        },
        """

        # [Create Testing] define object data
        # indicator_data = {
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
        #     'xid': '123.123.123.124',
        # }

        # [Create Testing] define object data
        indicator_data = {
            'active': True,
            'confidence': 75,
            'description': 'TcEx Testing',
            'ip': '123.123.123.124',
            'rating': 3,
            'source': None,
            'type': 'Address',
            'xid': '123.123.123.124',
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
            "name": "TLP:WHITE",
        }
        indicator.add_security_label(**security_label_data)

        # [Create Testing] define object data
        tag_data = {
            'name': 'TcEx Testing',
        }
        indicator.add_tag(**tag_data)

        # print(indicator.model.dict())
        try:
            indicator.submit()
        except RuntimeError:
            pass

        print('status_code', indicator.request.status_code)
        print('method', indicator.request.request.method)
        print('url', indicator.request.request.url)
        print('body', indicator.request.request.body)
        # print('text', indicator.request.text)

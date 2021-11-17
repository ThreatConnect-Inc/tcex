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
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestIndicators(TestV3):
    """Test TcEx API Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('indicators')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # cleanup between tests
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, 'pytest')
        for indicator in indicators:
            indicator.delete()

        # cleanup between tests
        groups = self.v3.groups()
        groups.filter.tag(TqlOperator.EQ, 'pytest')
        for group in groups:
            group.delete()

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
        indicator.stage_attribute(attribute_data)

        # [Create Testing] define object data
        security_label_data = {
            'name': 'TLP:WHITE',
        }
        indicator.stage_security_label(security_label_data)

        # [Create Testing] define object data
        tag_data = {
            'name': 'TcEx Testing',
        }
        indicator.stage_tag(tag_data)

        # print(indicator.model.dict())
        indicator.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        self.v3.indicator(id=indicator.model.id)

        # [Retrieve Testing] get the object from the API
        indicator.get(params={'fields': ['_all_']})

        for group in indicator.associated_groups:
            print('group name', group.model.name)

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
        # [Pre-Requisite] - create case
        indicator_count = 10
        indicator_ids = []
        indicator_tag = 'TcEx-Indicator-Testing'
        for _ in range(0, indicator_count):
            # [Create Testing] define object data
            indicator = self.v3_helper.create_indicator(
                **{
                    'active': True,
                    'associated_groups': {'id': 8755},
                    'attribute': {'type': 'Description', 'value': indicator_tag},
                    'confidence': randint(0, 100),
                    'description': 'TcEx Testing',
                    'rating': randint(0, 5),
                    'security_labels': {'name': 'TLP:WHITE'},
                    'source': None,
                    'tags': {'name': indicator_tag},
                    'type': 'Address',
                }
            )
            indicator_ids.append(indicator.model.id)

        # [Retrieve Testing] iterate over all object looking for needle
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, indicator_tag)
        # capture indicator count before deleting the indicator
        indicators_counts = len(indicators)
        for _, indicator in enumerate(indicators):
            assert indicator.model.id in indicator_ids
            indicator_ids.remove(indicator.model.id)

        assert indicators_counts == indicator_count
        assert not indicator_ids, 'Not all indicators were returned.'

    def test_indicator_address(self, request: FixtureRequest):
        """Test Artifact get single attached to task by id"""
        associated_indicator = self.v3_helper.create_indicator()
        associated_group = self.v3_helper.create_group(
            **{'associated_indicators': associated_indicator.model.gen_body(method='POST')}
        )

        # [Create testing] define object data
        indicator_data = {
            'active': True,
            'associated_groups': associated_group.model.gen_body(method='POST'),
            'attribute': {'type': 'Description', 'value': request.node.name},
            'confidence': randint(0, 100),
            'description': 'TcEx Testing',
            # for create indicator send value1 instead of ip
            'value1': f'123.{randint(1,255)}.{randint(1,255)}.{randint(1,255)}',
            'ownerName': 'TCI',
            'rating': randint(0, 5),
            'security_labels': {'name': 'TLP:WHITE'},
            'source': None,
            'tags': {'name': request.node.name},
            'type': 'Address',
        }

        # [Create testing] create a temporary indicator
        indicator = self.v3_helper.create_indicator(**indicator_data)

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        indicator = self.v3.indicator(id=indicator.model.id)

        # [Retrieve Testing] get the object from the API
        indicator.get(params={'fields': ['_all_']})

        # [Create Testing] testing setters on model
        indicator.model.active == indicator_data.get('active')
        # indicator.model.associated_groups == indicator_data.get('associated_groups')
        # indicator.model.associated_indicators == indicator_data.get('associated_indicators')
        # indicator.model.attributes == indicator_data.get('attributes')
        indicator.model.confidence == indicator_data.get('confidence')
        indicator.model.date_added is not None
        indicator.model.description == indicator_data.get('description')
        indicator.model.id == indicator_data.get('id')
        indicator.model.ip == indicator_data.get('value1')
        indicator.model.last_modified is not None
        indicator.model.owner_name == indicator_data.get('owner_name')
        indicator.model.rating == indicator_data.get('rating')
        # indicator.model.security_labels == indicator_data.get('security_labels')
        indicator.model.summary == indicator_data.get('summary')
        # indicator.model.tags == indicator_data.get('tags')
        indicator.model.type == indicator_data.get('type')
        indicator.model.web_link is not None

        # [Retrieve Testing] test as_entity
        assert indicator.as_entity.get('value') == indicator_data.get(
            'value1'
        ), 'as_entity test failed'

        # [Retrieve Testing] test associated_groups
        for ag in indicator.associated_groups:
            assert ag.model.name == associated_group.model.name

        # [Retrieve Testing] test associated_indicators
        for ai in indicator.associated_indicators:
            if ai.model.summary == indicator.model.summary:
                # found the associated indicator
                break
        else:
            assert False, f'Associated indicator {ai.model.summary} not found.'

    def test_indicator_get_many(self):
        """Test Indicators Get Many"""
        # [Pre-Requisite] - create case
        indicator_count = 10
        indicator_ids = []
        indicator_tag = 'TcEx-Indicator-Testing'
        for _ in range(0, indicator_count):
            # [Create Testing] define object data
            indicator = self.v3_helper.create_indicator(
                **{
                    'active': True,
                    'associated_groups': {'id': 8755},
                    'attribute': {'type': 'Description', 'value': indicator_tag},
                    'confidence': randint(0, 100),
                    'description': 'TcEx Testing',
                    'rating': randint(0, 5),
                    'security_labels': {'name': 'TLP:WHITE'},
                    'source': None,
                    'tags': {'name': indicator_tag},
                    'type': 'Address',
                }
            )
            indicator_ids.append(indicator.model.id)

        # [Retrieve Testing] iterate over all object looking for needle
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, indicator_tag)
        # capture indicator count before deleting the indicator
        indicators_counts = len(indicators)
        for _, indicator in enumerate(indicators):
            assert indicator.model.id in indicator_ids
            indicator_ids.remove(indicator.model.id)

        assert indicators_counts == indicator_count
        assert not indicator_ids, 'Not all indicators were returned.'

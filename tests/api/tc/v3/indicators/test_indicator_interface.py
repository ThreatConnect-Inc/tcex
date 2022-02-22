"""Test the TcEx API Module."""
# standard library
from random import randint, sample
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper

if TYPE_CHECKING:
    # third-party
    import pytest


class TestIndicators(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self, method: callable):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('indicators')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

        # remove an previous groups with the next test case name as a tag
        groups = self.tcex.v3.groups()
        groups.filter.tag(TqlOperator.EQ, method.__name__)
        for group in groups:
            group.delete()

        # remove an previous indicators with the next test case name as a tag
        indicators = self.v3.indicators()
        indicators.filter.tag(TqlOperator.EQ, method.__name__)
        for indicator in indicators:
            indicator.delete()

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

    # def test_return_indicators(self, request: 'pytest.FixtureRequest'):
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

    def test_indicator_create_and_retrieve_nested_types(self):
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
        assert indicator.model.summary == indicator_data.get('ip')
        assert indicator.model.ip == indicator_data.get('ip')

        # [Retrieve Testing] run assertions on returned nested data
        assert indicator.model.attributes.data[0].value == attribute_data.get('value')

        # [Retrieve Testing] run assertions on returned nested data
        assert indicator.model.security_labels.data[0].name == security_label_data.get('name')

        # [Retrieve Testing] run assertions on returned nested data
        assert indicator.model.tags.data[0].name == tag_data.get('name')

        # print('status_code', indicator.request.status_code)
        # print('method', indicator.request.request.method)
        # print('url', indicator.request.request.url)
        # print('body', indicator.request.request.body)
        # print('text', indicator.request.text)

    # def test_case_associations(self):
    #     """Test Indicator -> Case Associations"""
    #
    #     # [Pre-Requisite] - clean up past runs.
    #     cases = self.v3.cases()
    #     cases.filter.name(TqlOperator.IN, ['MyCase-20', 'MyCase-21', 'MyCase-22'])
    #
    #     for case in cases:
    #         case.delete()
    #
    #     # [Pre-Requisite] - create case
    #     case_2 = self.v3_helper.create_case(name='MyCase-20')
    #     case_3 = self.v3_helper.create_case(name='MyCase-21')
    #
    #     # [Create Testing] define object data
    #     indicator = self.v3.indicator(
    #         **{
    #             'ip': '43.24.65.49',
    #             'type': 'Address',
    #         }
    #     )
    #
    #     association_data = {'name': 'MyCase-22', 'severity': 'Low', 'status': 'Open'}
    #
    #     self.v3_helper._associations(indicator, case_2, case_3, association_data)
    #
    #     indicator.delete()
    #
    # def test_artifact_associations(self):
    #     """Test snippet"""
    #
    #     # self.v3_helper.tql_clear(['MyAdversary-03'], self.v3.groups())
    #     self.v3_helper.tql_clear(['MyCase-20'], self.v3.cases(), field='name')
    #
    #     case = self.v3_helper.create_case(name='MyCase-20')
    #
    #     # [Create Testing] define object data
    #     artifact = self.v3.artifact(
    #         **{
    #             'case_id': case.model.id,
    #             'intel_type': 'indicator-ASN',
    #             'summary': 'asn111',
    #             'type': 'ASN',
    #         }
    #     )
    #     artifact.create()
    #
    #     artifact_2 = self.v3.artifact(
    #         **{
    #             'case_id': case.model.id,
    #             'intel_type': 'indicator-ASN',
    #             'summary': 'asn112',
    #             'type': 'ASN',
    #         }
    #     )
    #     artifact_2.create()
    #
    #     artifact_3 = {
    #         'case_id': case.model.id,
    #         'intel_type': 'indicator-ASN',
    #         'summary': 'asn113',
    #         'type': 'ASN',
    #     }
    #
    #     indicator = self.v3.indicator(
    #         **{
    #             'ip': '43.243.63.18',
    #             'type': 'Address',
    #         }
    #     )
    #
    #     self.v3_helper._associations(indicator, artifact, artifact_2, artifact_3)
    #
    #     indicator.delete()

    def test_indicator_get_many(self, request: 'pytest.FixtureRequest'):
        """Test Indicators Get Many"""
        # [Pre-Requisite] - create case
        indicator_count = 10
        indicator_ids = []
        indicator_tag = request.node.name
        for _ in range(0, indicator_count):
            # [Create Testing] define object data
            indicator = self.v3_helper.create_indicator(
                **{
                    'active': True,
                    'attribute': {'type': 'Description', 'value': indicator_tag},
                    'confidence': randint(0, 100),
                    'description': 'TcEx Testing',
                    'rating': randint(1, 5),
                    'security_labels': {'name': 'TLP:WHITE'},
                    'source': None,
                    # automatically set by create_indicator
                    # 'tags': {'name': indicator_tag},
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

    def test_indicator_in_operator(self, request: 'pytest.FixtureRequest'):
        """Test Indicators Get Many"""
        # [Pre-Requisite] - create case
        indicator_count = 10
        indicator_ids = []
        indicator_addresses = []
        indicator_tag = request.node.name
        for _ in range(0, indicator_count):
            # [Create Testing] define object data
            indicator = self.v3_helper.create_indicator(
                **{
                    'active': True,
                    'attribute': {'type': 'Description', 'value': indicator_tag},
                    'confidence': randint(0, 100),
                    'description': 'TcEx Testing',
                    'rating': randint(1, 5),
                    'security_labels': {'name': 'TLP:WHITE'},
                    'source': None,
                    # automatically set by create_indicator
                    # 'tags': {'name': indicator_tag},
                    'type': 'Address',
                }
            )
            indicator_ids.append(indicator.model.id)
            indicator_addresses.append(indicator.model.ip)

        chosen_indicator_addresses = sample(indicator_addresses, 3)
        indicators = self.v3.indicators()
        indicators.filter.summary(TqlOperator.IN, chosen_indicator_addresses)
        # capture indicator count before deleting the indicator
        assert len(indicators) == 3

        # [TQLOperator.IN with String Testing] asset that the objects expected are returned
        for indicator in indicators:
            assert indicator.model.ip in chosen_indicator_addresses
            chosen_indicator_addresses.remove(indicator.model.ip)

        assert not chosen_indicator_addresses, 'Not all indicators addresses were returned'

        chosen_indicator_ids = sample(indicator_ids, 3)
        indicators = self.v3.indicators()
        indicators.filter.id(TqlOperator.IN, chosen_indicator_ids)
        assert len(indicators) == 3

        # [TQLOperator.IN with Int Testing] asset that the objects expected are returned
        for indicator in indicators:
            assert indicator.model.id in chosen_indicator_ids
            chosen_indicator_ids.remove(indicator.model.id)

        assert not chosen_indicator_ids, 'Not all indicators ids were returned'

    def test_indicator_address(self, request: 'pytest.FixtureRequest'):
        """Test Artifact get single attached to task by id"""
        associated_indicator = self.v3_helper.create_indicator()
        associated_group = self.v3_helper.create_group(
            **{
                'associated_indicators': associated_indicator.model.gen_body(
                    method='PUT', nested=True
                )
            }
        )

        # [Create testing] define object data
        indicator_data = {
            'active': True,
            'associated_groups': associated_group.model.gen_body(
                method='PUT', mode='append', nested=True
            ),
            'attribute': {'type': 'Description', 'value': request.node.name},
            'confidence': randint(0, 100),
            # for create indicator send value1 instead of ip
            'value1': f'123.{randint(1,255)}.{randint(1,255)}.{randint(1,255)}',
            'owner_name': 'TCI',
            'rating': randint(1, 5),
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
        assert indicator.model.active == indicator_data.get('active')
        # assert indicator.model.associated_groups == indicator_data.get('associated_groups')
        # assert indicator.model.associated_indicators == indicator_data.get(
        #     'associated_indicators'
        # )
        # assert indicator.model.attributes == indicator_data.get('attributes')
        assert indicator.model.confidence == indicator_data.get('confidence')
        assert indicator.model.date_added is not None
        assert indicator.model.ip == indicator_data.get('value1')
        assert indicator.model.last_modified is not None
        assert indicator.model.owner_name == indicator_data.get('owner_name')
        assert indicator.model.rating == indicator_data.get('rating')
        # assert indicator.model.security_labels == indicator_data.get('security_labels')
        assert indicator.model.summary == indicator_data.get('value1')
        # assert indicator.model.tags == indicator_data.get('tags')
        assert indicator.model.type == indicator_data.get('type')
        assert indicator.model.web_link is not None

        # [Retrieve Testing] test as_entity
        assert indicator.as_entity.get('value') == indicator_data.get(
            'value1'
        ), 'as_entity test failed'

        # [Retrieve Testing] test associated_groups
        for ag in indicator.associated_groups:
            assert ag.model.name == associated_group.model.name

        # [Retrieve Testing] test associated_indicators
        for ai in indicator.associated_indicators:
            if ai.model.summary == associated_indicator.model.summary:
                # found the associated indicator
                break
        else:
            assert False, f'Associated indicator {ai.model.summary} not found.'

"""TcEx Framework Module"""

# standard library
from collections.abc import Callable

# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestGroups(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('groups')

    def setup_method(self, method: Callable):
        """Configure setup before all tests."""
        super().setup_method()

        # remove an previous groups with the next test case name as a tag
        groups = self.tcex.api.tc.v3.groups()
        groups.filter.tag(TqlOperator.EQ, method.__name__)
        for group in groups:
            group.delete()

    def test_group_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_group_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_group_object_properties(self):
        """Test properties."""
        super().obj_properties()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_group_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_artifact_associations(self):
        """Test snippet"""

        self.v3_helper.tql_clear(['MyAdversary-03'], self.v3.groups())
        self.v3_helper.tql_clear(['MyCase-03'], self.v3.cases(), field='name')

        case = self.v3_helper.create_case(name='MyCase-03')

        # [Create Testing] define object data
        artifact = self.v3.artifact(
            **{
                'case_id': case.model.id,
                'intel_type': 'indicator-ASN',
                'summary': 'asn101',
                'type': 'ASN',
            }
        )
        artifact.create()

        artifact_2 = self.v3.artifact(
            **{
                'case_id': case.model.id,
                'intel_type': 'indicator-ASN',
                'summary': 'asn102',
                'type': 'ASN',
            }
        )
        artifact_2.create()

        artifact_3 = {
            'case_id': case.model.id,
            'intel_type': 'indicator-ASN',
            'summary': 'asn103',
            'type': 'ASN',
        }

        group = self.tcex.api.tc.v3.group(name='MyAdversary-03', type='Adversary')

        self.v3_helper._associations(group, artifact, artifact_2, artifact_3)

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_case_associations(self):
        """Test snippet"""

        self.v3_helper.tql_clear(['MyAdversary-02'], self.v3.groups())
        self.v3_helper.tql_clear(
            ['MyCase-00', 'MyCase-01', 'MyCase-02'], self.v3.cases(), field='name'
        )

        case = self.v3_helper.create_case(name='MyCase-00')
        case_2 = self.v3_helper.create_case(name='MyCase-01')
        case_3 = {'name': 'MyCase-02', 'severity': 'Low', 'status': 'Open'}

        group = self.tcex.api.tc.v3.group(
            name='MyAdversary-02',
            type='Adversary',
        )
        self.v3_helper._associations(group, case, case_2, case_3)

    def test_group_associations(self):
        """Test snippet"""

        self.v3_helper.tql_clear(
            ['MyAdversary-01', 'StagedGroup-00', 'StagedGroup-02'], self.v3.groups()
        )

        # [Pre-Requisite] - Create Groups
        staged_group = self.v3_helper.create_group(name='StagedGroup-00', xid='staged_group_00-xid')
        staged_group_2 = self.v3_helper.create_group(
            name='StagedGroup-02', xid='staged_group_02-xid'
        )

        group = self.tcex.api.tc.v3.group(
            name='MyAdversary-01',
            type='Adversary',
            associated_groups={
                'data': [
                    {'id': staged_group.model.id},
                    {'name': 'MyGroup-00', 'type': 'Adversary'},
                    {'name': 'MyGroup-02', 'type': 'Adversary'},
                ]
            },
        )
        group.create()

        # [Retrieve Testing] - Validate that the groups passed into the init are created.
        found_groups = 0
        for _ in group.associated_groups:
            found_groups += 1
        assert found_groups == 3

        # [Append Testing] - Stage a new group as a association
        group.stage_associated_group({'id': staged_group_2.model.id})
        group.update()

        # [Retrieve Testing] - Validate that the group staged is associated.
        found_groups = 0
        staged_group_found = False
        for associated_group in group.associated_groups:
            found_groups += 1
            if associated_group.model.id == staged_group_2.model.id:
                staged_group_found = True
        assert found_groups == 4, f'Invalid amount of groups ({found_groups}) retrieved'
        assert staged_group_found, 'Newly staged group not retrieved'

        group = self.v3.group(id=group.model.id)
        # [Stage Testing] - Stage a new group as a association
        group.stage_associated_group({'id': staged_group.model.id})
        # [Replace Testing] - Replace the current associations with the newly staged association
        group.update(mode='replace')

        # [Retrieve Testing] - Validate that only the staged group is associated.
        found_groups = 0
        for _ in group.associated_groups:
            found_groups += 1
        assert found_groups == 1

        group = self.v3.group(id=group.model.id)
        # [Stage Testing] - Stage a new group as a association
        group.stage_associated_group({'id': staged_group.model.id})
        # [Delete Testing] - Delete the newly staged association
        group.update(mode='delete')

        found_groups = 0
        for _ in group.associated_groups:
            found_groups += 1
        assert found_groups == 0

    def test_victim_asset_associations(self):
        """Test snippet"""

        self.v3_helper.tql_clear(
            ['MyAdversary-01', 'StagedGroup-00', 'StagedGroup-02'], self.v3.groups()
        )
        self.v3_helper.tql_clear(['MyVictim-01'], self.v3.victims())

        # [Pre-Requisite] - Create Groups
        staged_group = self.v3_helper.create_group(name='StagedGroup-00', xid='staged_group_00-xid')

        # [Pre-Requisite] - Create Groups
        staged_victim = self.v3_helper.create_victim(name='MyVictim-01')

        assert staged_victim.as_entity.get('id') is not None

        # Add attribute
        asset = self.tcex.api.tc.v3.victim_asset(
            type='EmailAddress', address='malware@example.com', address_type='Trojan'
        )
        staged_victim.stage_victim_asset(asset)

        staged_victim.update(params={'owner': 'TCI', 'fields': ['_all_']})

        assert asset.as_entity.get('type') == 'Victim Asset : EmailAddress'
        assert asset.as_entity.get('value') == 'Trojan : malware@example.com'
        assert staged_victim.model.assets.data is not None, 'No assets found'
        asset = staged_victim.model.assets.data[0]

        staged_group.stage_associated_victim_asset(asset)
        staged_group.update(params={'owner': 'TCI', 'fields': ['_all_']})

        found_victim_assets = 0
        staged_victim_asset_found = False
        for victim_asset in staged_group.associated_victim_assets:
            found_victim_assets += 1
            if victim_asset.model.id == asset.id:
                staged_victim_asset_found = True
        assert (
            found_victim_assets == 1
        ), f'Invalid amount of Victim Assets ({found_victim_assets}) retrieved'
        assert staged_victim_asset_found, 'Newly staged victim asset not retrieved'

    def test_group_create_and_retrieve_nested_types(self):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        groups = self.v3.groups()
        groups.filter.has_indicator.last_modified(TqlOperator.GT, '2021-11-09T00:00:00Z')
        groups.filter.owner_name(TqlOperator.EQ, 'TCI')

        # groups.filter.has_indicator.last_modified(TqlOperator.GT, 'yesterday')
        for group in groups:
            print(group.model.name)
            # print(group.blah.writable)
            # print(group.model.json(indent=4))
            # print(group.post_properties)
            # group.get(params={'fields': ['_all_']})
            # print(group.model.json(exclude_none=True, indent=2))
            # print('writable', group.results.writable)
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
        #     group.create()
        # except RuntimeError:
        #     pass
        # print('status_code', group.request.status_code)
        # print('method', group.request.request.method)
        # print('url', group.request.request.url)
        # print('body', group.request.request.body)
        # print('text', group.request.text)

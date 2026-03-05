"""TcEx Framework Module"""

import os
from datetime import datetime, timedelta

import pytest

from tcex import TcEx
from tcex.api.tc.v2.batch.association import Association
from tcex.api.tc.v3.tql.tql_operator import TqlOperator


class TestBatchAssociation:
    """Test the TcEx Batch Association Module."""

    staged_indicators: set
    staged_groups: set

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.staged_indicators = set()
        self.staged_groups = set()

    def cleanup(self, tcex: TcEx):
        """Test batch attributes creation"""
        groups = tcex.api.tc.v3.groups(
            params={'owner': os.getenv('TC_OWNER', 'TCI'), 'fields': ['associatedGroups']}
        )
        for group in groups:
            if group.model.name in self.staged_groups:
                group.delete()
                print(group.model.name)

        indicators = tcex.api.tc.v3.indicators(
            params={'owner': os.getenv('TC_OWNER', 'TCI'), 'fields': ['associatedGroups']}
        )
        for indicator in indicators:
            if indicator.model.summary in self.staged_indicators:
                indicator.delete()
                print(indicator.model.summary)

    def create_staged_data(self, data, batch):
        """Create staged data for testing."""

        def _stage_group_data(data_type, name):
            data = {'name': name, 'xid': name}
            if data_type == 'campaign':
                data['first_seen'] = (datetime.now() - timedelta(days=2)).isoformat()
                campaign = batch.campaign(**data)
                batch.save(campaign)
                return campaign
            return None

        def _stage_indicator_data(data_type, value1):
            data = {}
            if data_type == 'address':
                data['ip'] = value1
                ti = batch.address(**data)
            elif data_type == 'mutex':
                data['mutex'] = value1
                ti = batch.mutex(**data)
            else:
                return None
            batch.save(ti)
            return ti

        data_type = data['type'].lower()
        uuid = data.get('name', data.get('value1'))
        if not uuid:
            raise ValueError('Either name or value1 must be provided.')
        if data_type in {'campaign'}:
            campaign = _stage_group_data(data_type, uuid)
            self.staged_groups.add(campaign.name)
            return campaign
        if data_type in {'address', 'mutex'}:
            indicator = _stage_indicator_data(data_type, uuid)
            self.staged_indicators.add(indicator.summary)
            return indicator
        raise ValueError(f'Invalid data type: {data_type}')

    def resolve_association_variables(self, association_data, tcex):
        """Resolve variables in the association data."""
        for data in association_data:
            for key, value in data.items():
                if value.startswith('$id_of_name.'):
                    _, _, name = value.partition('.')
                    data[key] = self.get_id_by_name(name, tcex)
                if value.startswith('$id_of_summary.'):
                    _, _, summary = value.partition('.')
                    data[key] = self.get_id_by_summary(summary, tcex)
        return association_data

    def get_id_by_name(self, name, tcex):
        """Get the ID of a group by its name."""
        groups = tcex.api.tc.v3.groups(params={'owner': os.getenv('TC_OWNER', 'TCI')})
        groups.filter.summary(TqlOperator.EQ, name)
        for group in groups:
            if group.model.name == name:
                return group.model.id
        raise ValueError(f'Group with name {name} not found.')

    def get_id_by_summary(self, summary, tcex):
        """Get the ID of a group by its name."""
        indicators = tcex.api.tc.v3.indicators(params={'owner': os.getenv('TC_OWNER', 'TCI')})
        indicators.filter.summary(TqlOperator.EQ, summary)
        for indicator in indicators:
            if indicator.model.summary == summary:
                return indicator.model.id
        raise ValueError(f'Indicator with summary {summary} not found.')

    @pytest.mark.parametrize(
        'staged_data, association_data, expectation',
        [
            (
                [
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_1'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_2'},
                ],
                [
                    {
                        'ref_1': 'test_group_to_group_association_1',
                        'ref_2': 'test_group_to_group_association_2',
                    },
                ],
                1,
            ),
            (
                [
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_1'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_2'},
                ],
                [
                    {
                        'ref_1': 'test_group_to_group_association_1',
                        'ref_2': 'test_group_to_group_association_2',
                    },
                    {
                        'ref_2': 'test_group_to_group_association_1',
                        'ref_1': 'test_group_to_group_association_2',
                    },
                ],
                1,
            ),
            (
                [
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_1'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_2'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_3'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_4'},
                ],
                [
                    {
                        'ref_1': 'test_group_to_group_association_1',
                        'ref_2': 'test_group_to_group_association_2',
                    },
                    {
                        'ref_1': 'test_group_to_group_association_1',
                        'ref_2': 'test_group_to_group_association_3',
                    },
                    {
                        'ref_1': 'test_group_to_group_association_1',
                        'ref_2': 'test_group_to_group_association_4',
                    },
                ],
                3,
            ),
            (
                [
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_1'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_2'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_3'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_4'},
                ],
                [
                    {
                        'ref_1': 'test_group_to_group_association_2',
                        'ref_2': 'test_group_to_group_association_1',
                    },
                    {
                        'ref_1': 'test_group_to_group_association_3',
                        'ref_2': 'test_group_to_group_association_1',
                    },
                    {
                        'ref_1': 'test_group_to_group_association_4',
                        'ref_2': 'test_group_to_group_association_1',
                    },
                ],
                3,
            ),
            (
                [
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_1'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_2'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_3'},
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_4'},
                ],
                [
                    {
                        'id_1': '$id_of_name.test_group_to_group_association_2',
                        'ref_2': 'test_group_to_group_association_1',
                    },
                    {
                        'ref_1': 'test_group_to_group_association_3',
                        'id_2': '$id_of_name.test_group_to_group_association_1',
                    },
                    {
                        'ref_1': 'test_group_to_group_association_4',
                        'ref_2': 'test_group_to_group_association_1',
                    },
                ],
                3,
            ),
            (
                [
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_1'},
                    {'type': 'Address', 'value1': '94.102.49.190'},
                    {'type': 'Address', 'value1': '94.102.49.191'},
                    {'type': 'Mutex', 'value1': 'test_group_to_group_association_2'},
                ],
                [
                    {
                        'ref_1': 'test_group_to_group_association_1',
                        'id_2': '$id_of_summary.94.102.49.191',
                        'type_2': 'Address',
                    },
                    # {
                    #     'id_1': '$id_of_summary.94.102.49.190',
                    #     'type_1': 'Address',
                    #     'id_2': '$id_of_summary.94.102.49.191',
                    #     'type_2': 'Address',
                    #     'association_type': 'Address to Indicators',
                    # },
                    {
                        'id_1': '$id_of_summary.test_group_to_group_association_2',
                        'type_1': 'Mutex',
                        'id_2': '$id_of_summary.94.102.49.190',
                        'type_2': 'Address',
                        'association_type': 'Address to Indicators',
                    },
                ],
                2,
            ),
            (
                [
                    {'type': 'Campaign', 'name': 'test_group_to_group_association_1'},
                    {'type': 'Address', 'value1': '94.102.49.190'},
                    {'type': 'Address', 'value1': '94.102.49.191'},
                    {'type': 'Mutex', 'value1': 'test_group_to_group_association_2'},
                ],
                [
                    {
                        'ref_1': 'test_group_to_group_association_1',
                        'id_2': '$id_of_summary.94.102.49.191',
                        'type_2': 'Address',
                    },
                    {
                        'ref_2': 'test_group_to_group_association_1',
                        'id_1': '$id_of_summary.94.102.49.191',
                        'type_1': 'Address',
                    },
                    # {
                    #     'id_1': '$id_of_summary.94.102.49.190',
                    #     'type_1': 'Address',
                    #     'id_2': '$id_of_summary.94.102.49.191',
                    #     'type_2': 'Address',
                    #     'association_type': 'Address to Indicators',
                    # },
                    {
                        'id_1': '$id_of_summary.test_group_to_group_association_2',
                        'type_1': 'Mutex',
                        'id_2': '$id_of_summary.94.102.49.190',
                        'type_2': 'Address',
                        'association_type': 'Address to Indicators',
                    },
                ],
                2,
            ),
        ],
    )
    def test_association_as_kwargs(self, staged_data, association_data, expectation, tcex: TcEx):
        """Test batch attributes creation"""
        self.cleanup(tcex)
        batch = tcex.api.tc.v2.batch(owner=os.getenv('TC_OWNER', 'TCI'))
        for data in staged_data:
            self.create_staged_data(data=data, batch=batch)
        batch_status = batch.submit_all()
        data = self.resolve_association_variables(association_data, tcex)
        for data in association_data:
            batch.add_association(data)
        batch_status = batch.submit_all()[0]
        successful_associations = batch_status.get('successAssociationCount', 0)
        failed_associations = batch_status.get('errorAssociationCount', 0)
        assert (
            successful_associations == expectation
        ), f'Expected {expectation} successful associations, but got {successful_associations}'
        assert (
            failed_associations == 0
        ), f'Expected 0 failed associations, but got {failed_associations}'
        batch.close()

    @pytest.mark.parametrize(
        'association_1, association_2, expectation',
        [
            # Test case 1: Identical associations (should be treated as equal)
            (
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                True,
            ),
            # Test case 2: Same logical association but different order (should be treated as equal)
            (
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref2',
                    'type_1': 'type2',
                    'id_1': 2,
                    'ref_2': 'ref1',
                    'type_2': 'type1',
                    'id_2': 1,
                },
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                True,
            ),
            # Test case 3: Different associations (should not be treated as equal)
            (
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                {
                    'association_type': 'typeB',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                False,
            ),
            # Test case 4: One association has None values (should not be treated as equal)
            (
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': None,
                    'type_2': None,
                    'id_2': None,
                },
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                False,
            ),
            # Test case 5: Both associations have None values but are logically equal
            (
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': None,
                    'type_2': None,
                    'id_2': None,
                },
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': None,
                    'type_2': None,
                    'id_2': None,
                },
                True,
            ),
            # Test case 6: Associations with different `association_type` but same other fields
            (
                {
                    'association_type': 'typeA',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                {
                    'association_type': 'typeB',
                    'ref_1': 'ref1',
                    'type_1': 'type1',
                    'id_1': 1,
                    'ref_2': 'ref2',
                    'type_2': 'type2',
                    'id_2': 2,
                },
                False,
            ),
            # Test case 7: Associations with all fields None (should be treated as equal)
            (
                {
                    'association_type': None,
                    'ref_1': None,
                    'type_1': None,
                    'id_1': None,
                    'ref_2': None,
                    'type_2': None,
                    'id_2': None,
                },
                {
                    'association_type': None,
                    'ref_1': None,
                    'type_1': None,
                    'id_1': None,
                    'ref_2': None,
                    'type_2': None,
                    'id_2': None,
                },
                True,
            ),
        ],
    )
    def test_association_hashing(self, association_1, association_2, expectation):
        """Test the hashing and equality of Association objects."""
        associations = set()

        # Create Association objects
        assoc_1 = Association(**association_1)
        assoc_2 = Association(**association_2)

        # Add the first association to the set
        associations.add(assoc_1)

        # Check if the second association can be added to the set
        if expectation:
            assert (
                assoc_2 in associations
            ), 'Association 2 should be considered equal to Association 1.'
        else:
            assert (
                assoc_2 not in associations
            ), 'Association 2 should not be considered equal to Association 1.'

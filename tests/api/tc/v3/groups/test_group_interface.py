"""Test the TcEx API Module."""

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestGroups(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('groups')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

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

    def test_group_associations(self):
        """Test snippet"""

        groups = self.v3.groups()
        groups.filter.summary(
            TqlOperator.IN,
            [
                'MyAdversary',
                'StagedGroup1',
                'StagedGroup2',
            ],
        )
        for group in groups:
            group.delete()

        # [Pre-Requisite] - Create Groups
        staged_group = self.v3_helper.create_group(name='StagedGroup1', xid='staged_group-xid')
        staged_group_2 = self.v3_helper.create_group(name='StagedGroup2', xid='staged_group_2-xid')

        group = self.tcex.v3.group(
            name='MyAdversary',
            type='Adversary',
            associated_groups={
                'data': [
                    {'id': staged_group.model.id},
                    {'name': 'MyGroup0', 'type': 'Adversary'},
                    {'name': 'MyGroup', 'type': 'Adversary'},
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
        assert found_groups == 4, 'Invalid amount of groups retrieved'
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

    def test_group_create_and_retrieve_nested_types(self):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        groups = self.v3.groups()
        groups.filter.has_indicator.last_modified(TqlOperator.GT, '2021-11-09T00:00:00Z')

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

"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestOwnerSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('owners')

    def test_owner_get_all(self):
        """Test snippet"""
        # Begin Snippet
        for owner in self.tcex.api.tc.v3.owners():
            print(owner.model.dict(exclude_none=True))
        # End Snippet

    def test_owner_tql_filter(self):
        """Test snippet"""
        # Begin Snippet
        owners = self.tcex.api.tc.v3.owners()
        owners.filter.perm_apps(TqlOperator.EQ, 'BUILD')
        owners.filter.perm_artifact(TqlOperator.EQ, 'FULL')
        owners.filter.perm_attribute(TqlOperator.EQ, 'FULL')
        owners.filter.perm_attribute_type(TqlOperator.EQ, 'FULL')
        owners.filter.perm_case_tag(TqlOperator.EQ, 'FULL')
        owners.filter.perm_comment(TqlOperator.EQ, 'FULL')
        owners.filter.perm_copy_data(TqlOperator.EQ, 'FULL')
        owners.filter.perm_group(TqlOperator.EQ, 'FULL')
        owners.filter.perm_indicator(TqlOperator.EQ, 'FULL')
        owners.filter.perm_invite(TqlOperator.EQ, 'FULL')
        owners.filter.perm_members(TqlOperator.EQ, 'READ')
        owners.filter.perm_playbooks(TqlOperator.EQ, 'FULL')
        owners.filter.perm_playbooks_execute(TqlOperator.EQ, 'FULL')
        owners.filter.perm_post(TqlOperator.EQ, 'FULL')
        owners.filter.perm_publish(TqlOperator.EQ, 'FULL')
        owners.filter.perm_security_label(TqlOperator.EQ, 'FULL')
        owners.filter.perm_settings(TqlOperator.EQ, 'FULL')
        owners.filter.perm_tag(TqlOperator.EQ, 'FULL')
        owners.filter.perm_task(TqlOperator.EQ, 'FULL')
        owners.filter.perm_timeline(TqlOperator.EQ, 'FULL')
        owners.filter.perm_users(TqlOperator.EQ, 'FULL')
        owners.filter.perm_victim(TqlOperator.EQ, 'FULL')
        owners.filter.perm_workflow_template(TqlOperator.EQ, 'FULL')
        for owner in owners:
            print(owner.model.dict(exclude_none=True))
        # End Snippet

    def test_owner_get_by_id(self):
        """Test snippet"""
        # Begin Snippet
        owner = self.tcex.api.tc.v3.owner(id=3)
        owner.get()
        print(owner.model.dict(exclude_none=True))
        # End Snippet

        # self.v3_helper.tql_generator(owner.model, 'owner')
        # self.v3_helper.assert_generator(owner.model, 'owner')

        assert owner.model.id == 3
        assert owner.model.name == 'TCI'
        assert owner.model.owner_role == 'Organization Administrator'
        assert owner.model.perm_apps == 'BUILD'
        assert owner.model.perm_artifact == 'FULL'
        assert owner.model.perm_attribute == 'FULL'
        assert owner.model.perm_attribute_type == 'FULL'
        assert owner.model.perm_case_tag == 'FULL'
        assert owner.model.perm_comment == 'FULL'
        assert owner.model.perm_copy_data == 'FULL'
        assert owner.model.perm_group == 'FULL'
        assert owner.model.perm_indicator == 'FULL'
        assert owner.model.perm_invite == 'FULL'
        assert owner.model.perm_members == 'READ'
        assert owner.model.perm_playbooks == 'FULL'
        assert owner.model.perm_playbooks_execute == 'FULL'
        assert owner.model.perm_post == 'FULL'
        assert owner.model.perm_publish == 'FULL'
        assert owner.model.perm_security_label == 'FULL'
        assert owner.model.perm_settings == 'FULL'
        assert owner.model.perm_tag == 'FULL'
        assert owner.model.perm_task == 'FULL'
        assert owner.model.perm_timeline == 'FULL'
        assert owner.model.perm_users == 'FULL'
        assert owner.model.perm_victim == 'FULL'
        assert owner.model.perm_workflow_template == 'FULL'
        assert owner.model.type == 'Organization'

    @pytest.mark.parametrize(
        'name',
        [
            ('TCI'),
        ],
    )
    def test_cached_dict(self, name: str):
        """Test that the cached data contains the expected name."""
        # Manual runs of this test case return a runtime of 9 seconds when not cached and
        # less than 0.1 seconds when cached, so the cache is providing a significant performance
        # improvement.
        data = self.tcex.api.tc.v3.owners()
        assert name in data.cached_dict, f'Owner name {name!r} not found in cache'

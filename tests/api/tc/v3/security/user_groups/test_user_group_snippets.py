"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestUserGroupSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('user_groups')

    def test_user_group_get_all(self):
        """Test snippet"""
        # Begin Snippet
        for user_group in self.tcex.api.tc.v3.user_groups():
            print(user_group.model.dict(exclude_none=True))
        # End Snippet

    def test_user_group_tql_filter(self):
        """Test snippet"""
        # Begin Snippet
        user_groups = self.tcex.api.tc.v3.user_groups()
        user_groups.filter.name(TqlOperator.EQ, 'temp_user_group')
        for user_group in user_groups:
            print(user_group.model.dict(exclude_none=True))
        # End Snippet

    def test_user_group_get_by_id(self):
        """Test snippet"""
        # Begin Snippet
        user_group = self.tcex.api.tc.v3.user_group(id=1)
        user_group.get()
        print(user_group.model.dict(exclude_none=True))
        # End Snippet

    @pytest.mark.parametrize(
        'name',
        [
            ('TcEx Testing'),
        ],
    )
    def test_cached_dict(self, name: str):
        """Test that the cached data contains the expected name."""
        # Manual runs of this test case return a runtime of 9 seconds when not cached and
        # less than 0.1 seconds when cached, so the cache is providing a significant performance
        # improvement.
        data = self.tcex.api.tc.v3.user_groups()
        assert name in data.cached_dict, f'User group name {name!r} not found in cache'

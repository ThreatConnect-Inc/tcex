"""TcEx Framework Module"""

import pytest

from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestOwnerRolesSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('owner_roles')

    def test_owner_roles_get_all(self):
        """Test snippet"""
        # Begin Snippet
        for owner_role in self.tcex.api.tc.v3.owner_roles():
            print(owner_role.model.dict(exclude_none=True))
        # End Snippet

    def test_owner_roles_tql_filter(self):
        """Test snippet"""
        # Begin Snippet
        owner_roles = self.tcex.api.tc.v3.owner_roles()
        owner_roles.filter.available(TqlOperator.EQ, True)
        owner_roles.filter.comm_role(TqlOperator.EQ, False)
        owner_roles.filter.org_role(TqlOperator.EQ, True)
        for owner_role in owner_roles:
            print(owner_role.model.dict(exclude_none=True))
        # End Snippet

    def test_owner_role_get_by_id(self):
        """Test snippet"""
        # Begin Snippet
        owner_role = self.tcex.api.tc.v3.owner_role(id=1)
        owner_role.get()
        print(owner_role.model.dict(exclude_none=True))
        # End Snippet

    @pytest.mark.parametrize(
        'name',
        [
            ('App Developer'),
            ('Commenter'),
            ('Contributor'),
            ('Editor'),
            ('Director'),
            ('User'),
        ],
    )
    def test_cached_dict(self, name: str):
        """Test that the attribute type cache contains the expected name."""
        # Manual runs of this test case return a runtime of 9 seconds when not cached and
        # less than 0.1 seconds when cached, so the cache is providing a significant performance
        # improvement.
        data = self.tcex.api.tc.v3.owner_roles()
        assert name in data.cached_dict, f'Owner role {name!r} not found in cache'

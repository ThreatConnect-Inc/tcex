"""TcEx Framework Module"""

import pytest

from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestSystemRolesSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('system_roles')

    def test_system_roles_get_all(self):
        """Test snippet"""
        # Begin Snippet
        for system_role in self.tcex.api.tc.v3.system_roles():
            print(system_role.model.dict(exclude_none=True))
        # End Snippet

    def test_system_roles_tql_filter(self):
        """Test snippet"""
        # Begin Snippet
        system_roles = self.tcex.api.tc.v3.system_roles()
        system_roles.filter.active(TqlOperator.EQ, True)
        system_roles.filter.assignable(TqlOperator.EQ, True)
        system_roles.filter.displayed(TqlOperator.EQ, True)
        for system_role in system_roles:
            print(system_role.model.dict(exclude_none=True))
        # End Snippet

    def test_system_role_get_by_id(self):
        """Test snippet"""
        # Begin Snippet
        system_role = self.tcex.api.tc.v3.system_role(id=1)
        system_role.get()
        print(system_role.model.dict(exclude_none=True))
        # End Snippet


    @pytest.mark.parametrize(
        'name',
        [
            ('Administrator'),
            ('Api User'),
            ('Read Only User'),
            ('User'),
        ],
    )
    def test_cached_dict(self, name: str):
        """Test that the attribute type cache contains the expected name."""
        # Manual runs of this test case return a runtime of 9 seconds when not cached and
        # less than 0.1 seconds when cached, so the cache is providing a significant performance
        # improvement.
        data = self.tcex.api.tc.v3.system_roles()
        assert name in data.cached_dict, f'System role {name!r} not found in cache'

"""Test the TcEx API Snippets."""
# standard library
from collections.abc import Callable

# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestVictimSnippets(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('victims')

    def setup_method(self, method: Callable):  # pylint: disable=arguments-differ
        """Configure setup before all tests."""
        super().setup_method()

        # remove an previous indicators with the next test case name as a tag
        victims = self.v3.victims()
        victims.filter.tag(TqlOperator.EQ, method.__name__)
        for victim in victims:
            victim.delete()

    def test_victim_stage_asset(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim()

        # Begin Snippet
        # Add attribute
        asset = self.tcex.api.tc.v3.victim_asset(
            type='EmailAddress', address='malware@example.com', address_type='Trojan'
        )
        victim.stage_victim_asset(asset)

        victim.update(params={'owner': 'TCI'})
        # End Snippet

    def test_victim_add_group_association_to_asset(self):
        """Test snippet"""
        victim = self.v3_helper.create_victim(
            assets={
                'type': 'EmailAddress',
                'address': 'malware@example.com',
                'address_type': 'Trojan',
            },
        )
        if victim.model.assets.data is None:
            pytest.fail('No assets found on victim.')

        group = self.v3_helper.create_group()

        # Begin Snippet
        asset = self.tcex.api.tc.v3.victim_asset(id=victim.model.assets.data[0].id)
        asset.stage_associated_group(group)
        asset.update()

        for association in victim.associated_groups:
            print(association)
        # End Snippet

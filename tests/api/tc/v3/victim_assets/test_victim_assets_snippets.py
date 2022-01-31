"""Test the TcEx API Snippets."""
# third-party
import pytest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


@pytest.mark.xdist_group(name='victim-asset-snippets')
class TestVictimSnippets(TestV3):
    """Test TcEx API Interface."""

    example_pdf = None
    v3 = None

    def setup_method(self, method: callable):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('victims')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

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
        asset = self.tcex.v3.victim_asset(
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
        group = self.v3_helper.create_group()

        # Begin Snippet
        asset = self.tcex.v3.victim_asset(id=victim.model.assets.data[0].id)
        asset.stage_associated_group(group)
        asset.update()

        for association in victim.associated_groups:
            print(association)
        # End Snippet

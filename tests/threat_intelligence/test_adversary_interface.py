"""Test the TcEx Threat Intel Module."""
# standard library
import os
from random import randint

from .ti_helpers import TestThreatIntelligence, TIHelper


class TestAdversaryGroups(TestThreatIntelligence):
    """Test TcEx Adversary Groups."""

    group_type = 'Adversary'
    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.group_type)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_adversary_create(self):
        """Create a group using specific interface."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.adversary(**group_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve group for asserts
        group_data['unique_id'] = ti.unique_id
        ti = self.ti.adversary(**group_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get(ti.api_entity) == group_data.get(ti.api_entity)

        # cleanup group
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_adversary_update_associations(self):
        """Create a group using specific interface."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        adversary = self.ti.adversary(**group_data)
        adversary.create()

        indicator_data = {
            'hostName': self.ti_helper.rand_host(),
            'confidence': randint(0, 100),
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        host1 = self.ti.host(**indicator_data)
        host1.create()

        indicator_data = {
            'hostName': self.ti_helper.rand_host(),
            'confidence': randint(0, 100),
            'owner': self.owner,
            'rating': randint(0, 5),
        }
        host2 = self.ti.host(**indicator_data)
        host2.create()

        adversary.add_association(host1)
        adversary.add_association(host2)

        for indicator in adversary.indicator_associations():
            if indicator['type'] == 'Host':
                ti_host = self.ti.host(
                    hostName=indicator['summary'],
                    owner=self.owner,
                    dns_active=True,
                    whois_active=True,
                )
                r = ti_host.update()
                ti_host_data = r.json().get('data', {}).get('host', {})
                assert ti_host_data.get('dnsActive', 'false').lower() == 'true'
                assert ti_host_data.get('whoisActive', 'false').lower() == 'true'

    def tests_ti_adversary_add_attribute(self, request):
        """Test group add attribute."""
        super().group_add_attribute(request)

    def tests_ti_adversary_add_label(self):
        """Test group add label."""
        super().group_add_label()

    def tests_ti_adversary_add_tag(self, request):
        """Test group add tag."""
        super().group_add_tag(request)

    def tests_ti_adversary_delete(self):
        """Test group delete."""
        super().group_delete()

    def tests_ti_adversary_get(self):
        """Test group get with generic group method."""
        super().group_get()

    def tests_ti_adversary_get_filter(self):
        """Test group get with filter."""
        super().group_get_filter()

    def tests_ti_adversary_get_includes(self, request):
        """Test group get with includes."""
        super().group_get_includes(request)

    def tests_ti_adversary_get_attribute(self, request):
        """Test group get attribute."""
        super().group_get_attribute(request)

    def tests_ti_adversary_get_label(self):
        """Test group get label."""
        super().group_get_label()

    def tests_ti_adversary_get_tag(self, request):
        """Test group get tag."""
        super().group_get_tag(request)

    def tests_ti_adversary_update(self, request):
        """Test updating group metadata."""
        super().group_update(request)

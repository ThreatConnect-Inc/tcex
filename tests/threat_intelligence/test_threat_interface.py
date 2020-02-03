# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os

from .ti_helpers import TIHelper, TestThreatIntelligence


class TestThreatGroups(TestThreatIntelligence):
    """Test TcEx Threat Groups."""

    group_type = 'Threat'
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

    def tests_ti_threat_create(self):
        """Create a group using specific interface."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.threat(**group_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve group for asserts
        group_data['unique_id'] = ti.unique_id
        ti = self.ti.threat(**group_data)
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

    def tests_ti_threat_add_attribute(self, request):
        """Test group add attribute."""
        super().group_add_attribute(request)

    def tests_ti_threat_add_label(self):
        """Test group add label."""
        super().group_add_label()

    def tests_ti_threat_add_tag(self, request):
        """Test group add tag."""
        super().group_add_tag(request)

    def tests_ti_threat_delete(self):
        """Test group delete."""
        super().group_delete()

    def tests_ti_threat_get(self):
        """Test group get with generic group method."""
        super().group_get()

    def tests_ti_threat_get_filter(self):
        """Test group get with filter."""
        super().group_get_filter()

    def tests_ti_threat_get_includes(self, request):
        """Test group get with includes."""
        super().group_get_includes(request)

    def tests_ti_threat_get_attribute(self, request):
        """Test group get attribute."""
        super().group_get_attribute(request)

    def tests_ti_threat_get_label(self):
        """Test group get label."""
        super().group_get_label()

    def tests_ti_threat_get_tag(self, request):
        """Test group get tag."""
        super().group_get_tag(request)

    def tests_ti_threat_update(self, request):
        """Test updating group metadata."""
        super().group_update(request)

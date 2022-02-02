"""Test the TcEx Threat Intel Module."""
# standard library
import os

from .ti_helpers import TestThreatIntelligence, TIHelper


class TestEmailGroups(TestThreatIntelligence):
    """Test TcEx Email Groups."""

    group_type = 'Email'
    owner = os.getenv('TC_OWNER')
    required_fields = {
        'body': 'Pytest Email Body',
        'from_addr': 'pytest-from@example.com',
        'header': 'Pytest Email Header',
        'subject': 'Pytest Email Subject',
        'to': 'pytest-to@example.com',
    }
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.group_type, required_fields=self.required_fields)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def tests_ti_email_create(self):
        """Create a group using specific interface."""
        group_data = {
            'body': 'Pytest Email Body',
            'from_addr': self.ti_helper.rand_email_address(),
            'header': 'Pytest Email Header',
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
            'subject': 'Pytest Email Subject',
            'to': self.ti_helper.rand_email_address(),
        }
        ti = self.ti.email(**group_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve group for asserts
        group_data['unique_id'] = ti.unique_id
        ti = self.ti.email(**group_data)
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

    def tests_ti_email_add_attribute(self, request):
        """Test group add attribute."""
        super().group_add_attribute(request)

    def tests_ti_email_add_label(self):
        """Test group add label."""
        super().group_add_label()

    def tests_ti_email_add_tag(self, request):
        """Test group add tag."""
        super().group_add_tag(request)

    def tests_ti_email_delete(self):
        """Test group delete."""
        super().group_delete()

    def tests_ti_email_get(self):
        """Test group get with generic group method."""
        super().group_get()

    def tests_ti_email_get_filter(self):
        """Test group get with filter."""
        super().group_get_filter()

    def tests_ti_email_get_includes(self, request):
        """Test group get with includes."""
        super().group_get_includes(request)

    def tests_ti_email_get_attribute(self, request):
        """Test group get attribute."""
        super().group_get_attribute(request)

    def tests_ti_email_get_label(self):
        """Test group get label."""
        super().group_get_label()

    def tests_ti_email_get_tag(self, request):
        """Test group get tag."""
        super().group_get_tag(request)

    def tests_ti_email_update(self, request):
        """Test updating group metadata."""
        super().group_update(request)

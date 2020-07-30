# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
# standard library
import os
import random

from .ti_helpers import TestThreatIntelligence, TIHelper


class TestSignatureGroups(TestThreatIntelligence):
    """Test TcEx Signature Groups."""

    group_type = 'Signature'
    owner = os.getenv('TC_OWNER')
    file_types = ['Snort', 'Suricata', 'YARA', 'ClamAV', 'OpenIOC', 'CybOX', 'Bro', 'Regex', 'SPL']
    required_fields = {
        'file_name': 'pytest.pdf',
        'file_type': random.choice(file_types),
        'file_text': 'pytest signature text',
    }
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.group_type, required_fields=self.required_fields)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_signature_create(self):
        """Create a group using specific interface."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'file_type': random.choice(self.file_types),
            'file_text': 'pytest signature text',
            'owner': self.owner,
        }
        ti = self.ti.signature(**group_data)
        r = ti.create()
        assert ti.as_entity

        # assert response
        assert r.status_code == 201

        # retrieve group for asserts
        group_data['unique_id'] = ti.unique_id
        ti = self.ti.signature(**group_data)
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

    def tests_ti_signature_add_attribute(self, request):
        """Test group add attribute."""
        super().group_add_attribute(request)

    def tests_ti_signature_add_label(self):
        """Test group add label."""
        super().group_add_label()

    def tests_ti_signature_add_tag(self, request):
        """Test group add tag."""
        super().group_add_tag(request)

    def tests_ti_signature_delete(self):
        """Test group delete."""
        super().group_delete()

    def tests_ti_signature_get(self):
        """Test group get with generic group method."""
        super().group_get()

    def tests_ti_signature_get_filter(self):
        """Test group get with filter."""
        super().group_get_filter()

    def tests_ti_signature_get_includes(self, request):
        """Test group get with includes."""
        super().group_get_includes(request)

    def tests_ti_signature_get_attribute(self, request):
        """Test group get attribute."""
        super().group_get_attribute(request)

    def tests_ti_signature_get_label(self):
        """Test group get label."""
        super().group_get_label()

    def tests_ti_signature_get_tag(self, request):
        """Test group get tag."""
        super().group_get_tag(request)

    def tests_ti_signature_update(self, request):
        """Test updating group metadata."""
        super().group_update(request)

    #
    # Custom test cases
    #

    def tests_ti_signature_download(self):
        """Test downloading group signature."""
        helper_ti = self.ti_helper.create_group()
        r = helper_ti.download()

        assert r.status_code == 200
        assert r.text == self.required_fields.get('file_text')

    def tests_ti_signature_download_no_update(self):
        """Test downloading group signature on not created group."""
        group_data = {
            'name': self.ti_helper.rand_name(),
            'file_name': self.ti_helper.rand_filename(),
            'file_type': self.ti_helper.rand_signature_type(),
            'file_text': 'pytest signature text',
            'owner': self.owner,
        }
        ti = self.ti.signature(**group_data)

        # download signature (coverage)
        try:
            ti.download()
            assert False, 'failed to catch download on an signature with no id.'
        except RuntimeError:
            assert True, 'caught download call on an signature with no id'

# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os

from .ti_helpers import TIHelper, TestThreatIntelligence


class TestHashTagIndicators(TestThreatIntelligence):
    """Test TcEx Hash Tag Indicators."""

    api_entity = 'hashtag'
    api_branch = 'hashtags'
    indicator_field = 'Hashtag'
    indicator_type = 'Hashtag'
    owner = os.getenv('TC_OWNER')
    ti = None
    ti_helper = None
    tcex = None

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.indicator_type, self.indicator_field)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.ti_helper.cleanup()

    def tests_ti_hashtag_get_tag(self, request):
        """Test indicator get tag."""
        super().indicator_get_tag(request)

    def tests_ti_hashtag_update(self):
        """Test updating indicator metadata."""
        super().indicator_update()

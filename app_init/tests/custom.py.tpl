# -*- coding: utf-8 -*-
"""Custom test method Class."""


class Custom(object):
    """Custom test method class Apps."""

    def __init__(self):
        """Initialize class properties."""

    def setup_class(self, test_feature):
        """Run setup class code."""

    def setup_method(self, test_feature):
        """Run setup method code."""

    def teardown_class(self, test_feature):
        """Run teardown class code."""

    def teardown_method(self, test_feature):
        """Run teardown method code."""

    def test_method(self, test_feature, profile_data):
        """Run test method code."""

% if app_type=='CustomTrigger':
    def trigger(self, test_feature, profile_data):
        """Perform action to trigger the event."""
        event_data = pd.get('event_data')
% endif

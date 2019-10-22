# -*- coding: utf-8 -*-
"""Custom test method Class for app_type -> ${app_type}."""


class Custom(object):
    """Custom test method class Apps."""

    def __init__(self):
        """Initialize class properties."""

    def setup_class(self, test_feature):
        """Run setup class code."""
        % if app_type in ['triggerservice', 'webhooktriggerservice']:
        test_feature.args = {}

        # uncomment the following line to use static topics
        # self.client_topic = 'client-topic-123'
        # self.server_topic = 'server-topic-123'
        % endif

    def setup_method(self, test_feature):
        """Run setup method code."""

    def teardown_class(self, test_feature):
        """Run teardown class code."""

    def teardown_method(self, test_feature):
        """Run teardown method code."""

    % if app_type=='triggerservice':
    def trigger_method(self, test_feature, profile_data):
        """Perform action to trigger the event."""
        event_data = pd.get('event_data')
    % else:
    def test_method(self, test_feature, profile_data):
        """Run test method code."""
    % endif

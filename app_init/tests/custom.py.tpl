# -*- coding: utf-8 -*-
"""Custom test method Class for app_type -> ${app_type}."""


# pylint: disable=no-self-use,unused-argument
class Custom(object):
    """Custom test method class Apps."""

    def __init__(self):
        """Initialize class properties."""

    def setup_class(self, test_feature):
        """Run setup class code."""
        % if app_type in ['triggerservice', 'webhooktriggerservice']:
        test_feature.args = {}

        # uncomment and modify to control sleep times
        # test_feature.sleep_after_publish_config = 0.5
        # test_feature.sleep_after_publish_webhook_event = 0.5
        # test_feature.sleep_after_service_start = 5
        # test_feature.sleep_before_delete_config = 2
        # test_feature.sleep_before_shutdown = 0.5

        # uncomment the following line to use static topics
        # test_feature.client_topic = 'client-topic-123'
        # test_feature.server_topic = 'server-topic-123'
        % endif

    def setup_method(self, test_feature):
        """Run setup method code."""

    def teardown_class(self, test_feature):
        """Run teardown class code."""

    def teardown_method(self, test_feature):
        """Run teardown method code."""

    % if app_type in ['triggerservice']:
    def trigger_method(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Perform action to trigger the event."""

    def test_pre_create_config(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before create configs."""

    def test_pre_delete_config(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before delete configs."""

    % elif app_type in ['webhooktriggerservice']:
    def test_pre_create_config(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before create configs."""

    def test_pre_delete_config(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before delete configs."""

    def test_pre_webhook(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before webhook."""

    % else:
    def test_pre_run(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before App run method."""

    def test_pre_validate(self, test_feature, profile_data):  # pylint: disable=useless-super-delegation
        """Run test method code before test validation."""
    % endif

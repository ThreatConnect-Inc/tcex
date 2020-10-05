# -*- coding: utf-8 -*-
"""Custom test method Class for runtime_level -> ${runtime_level}."""
from typing import Optional

# pylint: disable=no-self-use,unused-argument
class Custom:
    """Custom test method class Apps."""

    def __init__(self):
        """Initialize class properties."""

    def setup_class(self, test_feature: object) -> None:
        """Run setup class code."""
        % if runtime_level in ['triggerservice', 'webhooktriggerservice']:
        test_feature.args = {}

        # set the App run method (multiprocess, subprocess (default), thread)
        # test_feature.service_run_method = 'subprocess'

        # uncomment and modify to control sleep times
        # test_feature.sleep_after_publish_config = 0.5
        # test_feature.sleep_after_publish_webhook_event = 0.5
        # test_feature.sleep_after_service_start = 5
        # test_feature.sleep_before_delete_config = 2
        # test_feature.sleep_before_shutdown = 0.5

        # uncomment the following line to use static topics
        # test_feature.client_topic = 'client-topic-123'
        # test_feature.server_topic = 'server-topic-123'
        % else:
        # set the App run method (inline (default), subprocess)
        # Note: using inline forces the App to use the tcex version
        # from site-packages and not the lib_ directory.
        # test_feature.run_method = 'inline'
        % endif

    def setup_method(self, test_feature: object) -> None:
        """Run setup method code."""

    def teardown_class(self, test_feature: object) -> None:
        """Run teardown class code."""

    def teardown_method(self, test_feature: object) -> None:
        """Run teardown method code."""

    % if runtime_level in ['triggerservice']:
    def trigger_method(
        self, test_feature: object, profile_data: dict, monkeypatch: object
    ) -> None:  # pylint: disable=useless-super-delegation
        """Perform action to trigger the event."""
        # trigger = profile_data.get('trigger')

    def test_pre_create_config(
        self, test_feature: object, profile_data: dict, monkeypatch: object
    ) -> None:  # pylint: disable=useless-super-delegation
        """Run test method code before create configs."""

    def test_pre_delete_config(
        self, test_feature: object, profile_data: dict, monkeypatch: object
    ) -> None:  # pylint: disable=useless-super-delegation
        """Run test method code before delete configs."""

    % elif runtime_level in ['webhooktriggerservice']:
    def test_pre_create_config(
        self, test_feature: object, profile_data: dict, monkeypatch: object
    ) -> None:  # pylint: disable=useless-super-delegation
        """Run test method code before create configs."""

    def test_pre_delete_config(
        self, test_feature: object, profile_data: dict, monkeypatch: object
    ) -> None:  # pylint: disable=useless-super-delegation
        """Run test method code before delete configs."""

    def test_pre_webhook(
        self, test_feature: object, profile_data: dict, monkeypatch: object
    ) -> None:  # pylint: disable=useless-super-delegation
        """Run test method code before webhook."""

    % else:
    def test_pre_run(
        self, test_feature: object, profile_data: dict, monkeypatch: Optional[object]
    ) -> None:  # pylint: disable=useless-super-delegation
        """Run test method code before App run method."""
        if test_feature.run_method != 'inline':
            test_feature.log.warning('run_method is not inline, monkeypatch will not work!')

    def test_pre_validate(
        self, test_feature: object, profile_data: dict
    ) -> None:  # pylint: disable=useless-super-delegation
        """Run test method code before test validation."""
    % endif

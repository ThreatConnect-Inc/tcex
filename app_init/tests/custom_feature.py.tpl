# -*- coding: utf-8 -*-
"""Custom test method feature class."""
from ..custom import Custom  # pylint: disable=relative-beyond-top-level


class CustomFeature(Custom):
    """Custom test method class Apps."""

    def __init__(self, **kwargs):  # pylint: disable=useless-super-delegation
        """Initialize class properties."""
        super(CustomFeature, self).__init__(**kwargs)

    def setup_class(self, test_feature):  # pylint: disable=useless-super-delegation
        """Run setup class code."""
        super(CustomFeature, self).setup_class(test_feature)

    def setup_method(self, test_feature):  # pylint: disable=useless-super-delegation
        """Run setup method code."""
        super(CustomFeature, self).setup_method(test_feature)

    def teardown_class(self, test_feature):  # pylint: disable=useless-super-delegation
        """Run teardown class code."""
        super(CustomFeature, self).teardown_class(test_feature)

    def teardown_method(self, test_feature):  # pylint: disable=useless-super-delegation
        """Run teardown method code."""
        super(CustomFeature, self).teardown_method(test_feature)

    % if app_type in ['triggerservice']:
    def trigger_method(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Perform action to trigger the event."""
        super(CustomFeature, self).trigger_method(test_feature, profile_data, monkeypatch)

    % elif app_type in ['webhooktriggerservice']:
    def test_pre_create_config(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before create configs."""
        super(CustomFeature, self).test_pre_create_config(test_feature, profile_data, monkeypatch)

    def test_pre_delete_config(self, test_feature, profile_data):  # pylint: disable=useless-super-delegation
        """Run test method code before delete configs."""
        super(CustomFeature, self).test_pre_delete_config(test_feature, profile_data)

    def test_pre_webhook(self, test_feature, profile_data):  # pylint: disable=useless-super-delegation
        """Run test method code before webhook."""
        super(CustomFeature, self).test_pre_delete_config(test_feature, profile_data)

    % else:
    def test_pre_run(self, test_feature, profile_data, monkeypatch):  # pylint: disable=useless-super-delegation
        """Run test method code before App run method."""
        super(CustomFeature, self).test_pre_run(test_feature, profile_data, monkeypatch)

    def test_pre_validate(self, test_feature, profile_data):  # pylint: disable=useless-super-delegation
        """Run test method code before test validation."""
        super(CustomFeature, self).test_pre_validate(test_feature, profile_data)
    % endif

# -*- coding: utf-8 -*-
"""Custom test method feature class."""
from ..custom import Custom  # pylint: disable=relative-beyond-top-level


class CustomFeature(Custom):
    """Custom test method class Apps."""

    def __init__(self, **kwargs):  # pylint: disable=useless-super-delegation
        """Initialize class properties."""
        super(CustomFeature, self).__init__(**kwargs)

    def setup_class(self, test_feature):
        """Run setup class code."""
        super(CustomFeature, self).setup_class(test_feature)

    def setup_method(self, test_feature):
        """Run setup method code."""
        super(CustomFeature, self).setup_method(test_feature)

    def teardown_class(self, test_feature):
        """Run teardown class code."""
        super(CustomFeature, self).teardown_class(test_feature)

    def teardown_method(self, test_feature):
        """Run teardown method code."""
        super(CustomFeature, self).teardown_method(test_feature)

    % if app_type=='triggerservice':
    def trigger_method(self, test_feature, profile_data):
        """Perform action to trigger the event."""
        super(CustomFeature, self).trigger_method(test_feature, profile_data)
    % else:
    def test_method(self, test_feature, profile_data):
        """Run test method code."""
        super(CustomFeature, self).test_method(test_feature, profile_data)
    % endif

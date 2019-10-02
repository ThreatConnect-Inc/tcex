# -*- coding: utf-8 -*-
"""Test case template for App testing."""
# flake8: noqa: F401
import os
import sys
import time

import paho.mqtt.client as mqtt
import pytest
from ..profiles import profiles
${parent_import}  # pylint: disable=C0411
from .validate_feature import ValidateFeature  # pylint: disable=E0402

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)  # noqa: F821; pylint: disable=E0602
    sys.setdefaultencoding('utf-8')  # pylint: disable=no-member

# get profile names
profile_names = profiles(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.d'))

# pylint: disable=W0235,too-many-function-args
class TestFeature(${parent_class}):
    """TcEx App Testing Template."""

    @classmethod
    def setup_class(cls):
        """Run setup logic before all test cases in this module."""
        super(TestFeature, cls).setup_class()
        cls.args = {'hostname': 'localhost', 'port': 1883, 'timeout': 60}

        # uncomment the following line to use static topics
        cls.client_topic = 'client-topic-123'
        cls.server_topic = 'server-topic-123'

    def setup_method(self):
        """Run setup logic before test method runs."""
        super(TestFeature, self).setup_method()

    @classmethod
    def teardown_class(cls):
        """Run setup logic after all test cases in this module."""
        super(TestFeature, cls).teardown_class()

    def teardown_method(self):
        """Run teardown logic after test method completes."""
        super(TestFeature, self).teardown_method()

    def trigger_event(self, **kwargs):
        """Add custom code here to trigger event."""

    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name):
        """Run pre-created testing profiles."""

        # profile data
        pd = self.profile(profile_name)

        # publish createConfig
        for config in pd.get('configs'):
            self.publish_create_config(config.get('trigger_id'), config.get('config'))

        # !! trigger custom event here !!
        # self.trigger_event()

        # !! webhook trigger event !!
        # event = {
        #     'command': 'WebhookEvent',
        #     'method': 'GET',
        #     'queryParams': {'name': 'level', 'value': 'DEBUG'},
        #     'headers': {'name': 'content-type', 'value': 'application/json'},
        #     'body': 'body123',
        #     'requestKey': 'abc123',
        # }
        # self.publish(json.dumps(event)

        # publish deleteConfig
        for config in pd.get('configs'):
            self.publish_delete_config(config.get('trigger_id'))

        # populate output variables (if not already populated)
        self.populate_output_variables(pd)

        # run output variable validation
        ValidateFeature(self.validator).validate(pd.get('outputs'))

    def test_shutdown(self):
        """Run shutdown command."""
        self.publish_shutdown()

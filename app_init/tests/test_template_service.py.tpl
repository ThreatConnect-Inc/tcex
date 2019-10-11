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
from .trigger_event_feature import TriggerEventFeature
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
        trigger_event = TriggerEventFeature(**kwargs)
        trigger_event.trigger(**kwargs

    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name):
        """Run pre-created testing profiles."""

        # profile data
        pd = self.profile(profile_name)

        # publish createConfig
        for config in pd.get('configs'):
            self.publish_create_config(config)

        # trigger custom event
        trigger_event(pd.get('event_data'))

        # publish deleteConfig
        for config in pd.get('configs'):
            self.publish_delete_config(config)

        # run output variable validation
        for context in self.context_tracker:
            self.validator.tcex.default_args.tc_playbook_db_context = context
            trigger_id = self.redis_client.hget(context, '_trigger_id').decode('utf-8')
            output_data = (pd.get('outputs') or {}).get(trigger_id)
            if output_data is not None:
                ValidateFeature(self.validator).validate(output_data)

    def test_shutdown(self):
        """Run shutdown command."""
        self.publish_shutdown()

# -*- coding: utf-8 -*-
"""Test case template for App testing."""
# flake8: noqa: F401
import os
import sys

% if app_type=='triggerservice':
import paho.mqtt.client as mqtt
% endif

import pytest
from ..profiles import profiles
from tcex.testing import ${class}

from .custom_feature import CustomFeature  # pylint: disable=E0402
from .validate_feature import ValidateFeature  # pylint: disable=E0402

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)  # noqa: F821; pylint: disable=E0602
    sys.setdefaultencoding('utf-8')  # pylint: disable=no-member

# get profile names
profile_names = profiles(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.d'))


# pylint: disable=W0235,too-many-function-args
class TestProfiles(${class}):
    """TcEx App Testing Template."""

    def setup_class(self):
        """Run setup logic before all test cases in this module."""
        super(TestProfiles, self).setup_class()
        self.custom = CustomFeature()
        if os.getenv('SETUP_CLASS') is None:
            self.custom.setup_class(self)

        % if app_type=='triggerservice':
        # uncomment the following line to use static topics
        self.client_topic = 'client-topic-123'
        self.server_topic = 'server-topic-123'
        % endif

    def setup_method(self):
        """Run setup logic before test method runs."""
        super(TestProfiles, self).setup_method()
        if os.getenv('SETUP_METHOD') is None:
            self.custom.setup_method(self)

    def teardown_class(self):
        """Run setup logic after all test cases in this module."""
        super(TestProfiles, self).teardown_class()
        if os.getenv('TEARDOWN_CLASS') is None:
            self.custom.teardown_class(self)

    def teardown_method(self):
        """Run teardown logic after test method completes."""
        super(TestProfiles, self).teardown_method()
        if os.getenv('TEARDOWN_METHOD') is None:
            self.custom.teardown_method(self)

    % if app_type=='triggerservice':
    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name):
        """Run pre-created testing profiles."""

        # profile data
        pd = self.profile(profile_name)

        # publish createConfig
        for config in pd.get('configs'):
            self.publish_create_config(config)

        # trigger custom event
        self.custom.trigger(self, pd)

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
    % else:
    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name):  # pylint: disable=unused-argument
        """Run pre-created testing profiles."""
        # get profile
        pd = self.profile(profile_name)

        # check profile env
        self.check_environment(pd.get('environments', ['build']))

        # run custom test method
        custom.test_method(self, pd)

        assert self.run_profile(pd) in pd.get('exit_codes', [0])
        ValidateFeature(self.validator).validate(pd.get('outputs'))
        % if app_type=='organization':
        self.validator.threatconnect.batch(
            self.context, self.owner(pd), pd.get('validation_criteria', {})
        )
        % endif
    % endif

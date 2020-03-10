# -*- coding: utf-8 -*-
"""Test case template for App testing."""
# flake8: noqa: F401
import os

import pytest
from tcex.testing import ${class_name}
from ..profiles import profiles

from .custom_feature import CustomFeature  # pylint: disable=relative-beyond-top-level
from .validate_feature import ValidateFeature  # pylint: disable=relative-beyond-top-level

# get profile names
profile_names = profiles(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.d'))


# pylint: disable=useless-super-delegation,too-many-function-args
class TestProfiles(${class_name}):
    """TcEx App Testing Template."""

    def setup_class(self):
        """Run setup logic before all test cases in this module."""
        super(TestProfiles, self).setup_class()
        self.custom = CustomFeature()  # pylint: disable=attribute-defined-outside-init
        if os.getenv('SETUP_CLASS') is None:
            self.custom.setup_class(self)
        # enable auto-update of profile data
        self.enable_update_profile = True  # pylint: disable=attribute-defined-outside-init

    def setup_method(self):
        """Run setup logic before test method runs."""
        super(TestProfiles, self).setup_method()
        if os.getenv('SETUP_METHOD') is None:
            self.custom.setup_method(self)

    def teardown_class(self):
        """Run setup logic after all test cases in this module."""
        if os.getenv('TEARDOWN_CLASS') is None:
            self.custom.teardown_class(self)
        super(TestProfiles, self).teardown_class()
        # disable auto-update of profile data
        self.enable_update_profile = False  # pylint: disable=attribute-defined-outside-init

    def teardown_method(self):
        """Run teardown logic after test method completes."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.custom.teardown_method(self)
        super(TestProfiles, self).teardown_method()

    % if app_type in ['triggerservice', 'webhooktriggerservice']:
    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name, monkeypatch):
        """Run pre-created testing profiles."""

        # profile data
        profile_data = self.profile(profile_name)

        # call pre-configuration setup per test
        self.custom.test_pre_create_config(self, profile_data, monkeypatch)

        # publish createConfig
        for config in profile_data.get('configs'):
            self.publish_create_config(config)

        % if app_type == 'webhooktriggerservice':
        # call pre-configuration setup per test
        self.custom.test_pre_webhook(self, profile_data, monkeypatch)

        # send webhook event
        self.publish_webhook_event(**profile_data.get('webhook_event'))
        % else:
        # trigger custom event
        self.custom.trigger_method(self, profile_data, monkeypatch)
        % endif

        # call pre-configuration setup or validation per test
        self.custom.test_pre_delete_config(self, profile_data, monkeypatch)

        # publish deleteConfig
        for config in profile_data.get('configs'):
            self.publish_delete_config(config)

        # fail if there are no executions to validate
        # if not self.context_tracker and profile_data.get('outputs'):
        #     assert False, 'No context found in context_tracker, did event fire?'

        # run output variable validation
        for context in self.context_tracker:
            # for service Apps the context on playbooks needs to be set manually
            self.validator.tcex.playbook.key_value_store.context = context
            # the trigger id is stored via the monkey patched session_id method
            trigger_id = self.redis_client.hget(context, '_trigger_id').decode('utf-8')
            output_data = (profile_data.get('outputs') or {}).get(trigger_id)
            if output_data is not None:
                ValidateFeature(self.validator).validate(output_data)

        # exit message can not be validated since it's written during teardown for Service Apps

    % else:
    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name, monkeypatch):  # pylint: disable=unused-argument
        """Run pre-created testing profiles."""
        # get profile
        profile_data = self.profile(profile_name)

        # check profile env
        self.check_environment(profile_data.get('environments', ['build']))

        # run custom test method before run method
        self.custom.test_pre_run(self, profile_data, monkeypatch)

        assert self.run_profile(profile_data) in profile_data.get('exit_codes', [0])

        % if app_type=='organization':
        self.validator.threatconnect.batch(
            self.context, self.owner(profile_data), profile_data.get('validation_criteria', {})
        )
        % else:
        # run custom test method before validation
        self.custom.test_pre_validate(self, profile_data)

        ValidateFeature(self.validator).validate(profile_data.get('outputs'))
        % endif

        # validate exit message
        exit_message_data = profile_data.get('exit_message')
        if exit_message_data:
            self.validate_exit_message(
                exit_message_data.pop('expected_output'),
                exit_message_data.pop('op'),
                **exit_message_data
            )
    % endif

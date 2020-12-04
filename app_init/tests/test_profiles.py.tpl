# -*- coding: utf-8 -*-
"""Test case template for App testing."""
# flake8: noqa: F401
import os

from tcex.testing import ${class_name}

from .custom_feature import CustomFeature  # pylint: disable=relative-beyond-top-level
% if runtime_level!='organization':
from .validate_feature import ValidateFeature  # pylint: disable=relative-beyond-top-level
% endif


# pylint: disable=useless-super-delegation,too-many-function-args
class TestProfiles(${class_name}):
    """TcEx App Testing Template."""

    def setup_class(self) -> None:
        """Run setup logic before all test cases in this module."""
        super(TestProfiles, self).setup_class()
        self.custom = CustomFeature()  # pylint: disable=attribute-defined-outside-init
        if os.getenv('SETUP_CLASS') is None:
            self.custom.setup_class(self)
        # enable auto-update of profile data
        self.enable_update_profile = True  # pylint: disable=attribute-defined-outside-init

    def setup_method(self) -> None:
        """Run setup logic before test method runs."""
        super(TestProfiles, self).setup_method()
        if os.getenv('SETUP_METHOD') is None:
            self.custom.setup_method(self)

    def teardown_class(self) -> None:
        """Run setup logic after all test cases in this module."""
        if os.getenv('TEARDOWN_CLASS') is None:
            self.custom.teardown_class(self)
        super(TestProfiles, self).teardown_class()
        # disable auto-update of profile data
        self.enable_update_profile = False  # pylint: disable=attribute-defined-outside-init

    def teardown_method(self) -> None:
        """Run teardown logic after test method completes."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.custom.teardown_method(self)
        super(TestProfiles, self).teardown_method()

    % if runtime_level in ['triggerservice', 'webhooktriggerservice']:
    def test_profiles(
        self, profile_name: str, pytestconfig: object, monkeypatch: object, options: object
    ) -> None:  # pylint: disable=unused-argument
        """Run pre-created testing profiles."""

        # initialize profile
        valid, message = self.init_profile(
            profile_name, pytestconfig=pytestconfig, monkeypatch=monkeypatch,
            options=options
        )
        assert valid, message

        # call pre-configuration setup per test
        self.custom.test_pre_create_config(self, self.profile.data, monkeypatch)

        # publish createConfig
        for config in self.profile.configs:
            self.publish_create_config(config)

        % if runtime_level == 'webhooktriggerservice':
        # call pre-configuration setup per test
        self.custom.test_pre_webhook(self, self.profile.data, monkeypatch)

        # send webhook event
        self.publish_webhook_event(**self.profile.webhook_event)

        # send webhook marshall event
        if self.ij.has_feature('webhookresponsemarshall'):
            self.publish_marshall_webhook_event(**self.profile.webhook_marshall_event)
        % else:
        # trigger custom event
        self.custom.trigger_method(self, self.profile.data, monkeypatch)
        % endif

        # call pre-configuration setup or validation per test
        self.custom.test_pre_delete_config(self, self.profile.data, monkeypatch)

        # publish deleteConfig
        for config in self.profile.configs:
            self.publish_delete_config(config)

        # fail if there are no executions to validate
        if not self.profile.context_tracker and self.profile.outputs:
            assert False, 'No context found in context_tracker, did event fire?'

        # run output variable validation
        for context in self.profile.context_tracker:
            # get Validation instance
            validation = ValidateFeature(self.validator)
            # for service Apps the context on playbooks needs to be set manually
            self.validator.tcex.playbook._context = context
            # the trigger id is stored via the monkey patched session_id method
            trigger_id = self.redis_client.hget(context, '_trigger_id').decode('utf-8')
            output_data = (self.profile.outputs or {}).get(trigger_id)
            if output_data is not None:
                validation.validate(output_data)

            # validate App outputs and Profile outputs are consistent
            validation.validate_outputs(self.profile.tc_playbook_out_variables, output_data)

        # exit message can not be validated since it's written during teardown for Service Apps

    % else:
    def test_profiles(
        self, profile_name: str, pytestconfig: object, monkeypatch: object, options: object
    ) -> None:  # pylint: disable=unused-argument
        """Run pre-created testing profiles."""

        # initialize profile
        valid, message = self.init_profile(
            profile_name, pytestconfig=pytestconfig, monkeypatch=monkeypatch,
            options=options
        )
        assert valid, message

        # run custom test method before run method
        self.custom.test_pre_run(
            self,
            self.profile.data,
            monkeypatch if self.run_method == 'inline' else None)

        assert self.run_profile() in self.profile.exit_codes

        # run custom test method before validation
        self.custom.test_pre_validate(self, self.profile.data)

        % if runtime_level=='organization':
        self.validator.threatconnect.batch(self.profile)
        % else:
        # get Validation instance
        validation = ValidateFeature(self.validator)

        # validate App outputs and Profile outputs are consistent
        validation.validate_outputs(self.profile.tc_playbook_out_variables, self.profile.outputs)

        # validate App outputs with Profile outputs
        validation.validate(self.profile.outputs)
        % endif

        # validate exit message
        exit_message_data = self.profile.exit_message
        if exit_message_data:
            self.validate_exit_message(
                exit_message_data.pop('expected_output'),
                exit_message_data.pop('op'),
                **exit_message_data
            )
    % endif

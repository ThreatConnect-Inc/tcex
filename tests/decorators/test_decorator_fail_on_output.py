# -*- coding: utf-8 -*-
"""Test the TcEx FailOnOutput Decorator."""
# third-party
import pytest

# first-party
from tcex import FailOnOutput


# pylint: disable=no-self-use
class TestFailOnOutputDecorator:
    """Test the TcEx Decorators."""

    args = None
    exit_message = None
    fail_msg = None
    tcex = None

    @FailOnOutput(
        fail_enabled='fail_on_error',
        fail_msg='Failed due to invalid output',
        fail_msg_property='fail_msg',
        fail_on=[None, ''],
    )
    def fail_on_output(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('value')

    @pytest.mark.parametrize(
        'value', [(None), ([None]), (''), ([''])],
    )
    def test_fail_on_output(self, value, playbook_app):
        """Test FailOnOutput decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        self.fail_msg = f'Failed due to invalid output {value}'

        # call decorated method and get result
        try:
            self.fail_on_output(value=value)
            assert False, f'failed to catch invalid value {value}'
        except SystemExit as e:
            assert e.code == 1
            # must match default value in decorator or value passed to decorator
            assert self.exit_message == self.fail_msg

    @pytest.mark.parametrize(
        'value', [('good data')],
    )
    def test_fail_on_output_pass(self, value, playbook_app):
        """Test FailOnOutput decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # call decorated method and get result
        assert self.fail_on_output(value=value) == value

    def write_output(self):
        """Pass for coverage of write_output input."""

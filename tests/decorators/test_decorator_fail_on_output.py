# -*- coding: utf-8 -*-
"""Test the TcEx FailOnOutput Decorator."""
import pytest
from tcex import FailOnOutput


# pylint: disable=no-self-use
class TestFailOnOutputDecorator:
    """Test the TcEx Decorators."""

    args = None
    tcex = None

    @FailOnOutput(
        fail_enabled='fail_on_error', fail_msg='Failed due to invalid output', fail_on=[None, ''],
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

        # call decorated method and get result
        try:
            self.fail_on_output(value=value)
            assert False, f'failed to catch invalid value {value}'
        except RuntimeError as e:
            assert e.args[0] == 'Failed due to invalid output'  # must match fail_msg on decorator

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

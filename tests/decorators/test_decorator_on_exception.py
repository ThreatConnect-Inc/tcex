# -*- coding: utf-8 -*-
"""Test the TcEx Debug Decorator."""
# first-party
from tcex import OnException


# pylint: disable=no-self-use
class TestIterateOnArgDecorators:
    """Test the TcEx Decorators."""

    args = None
    exit_message = None
    tcex = None

    @OnException(exit_msg='on_exception method failed', exit_enabled='fail_on_error')
    def on_exception(self):
        """Test fail on input decorator with no arg value (use first arg input)."""
        raise AttributeError()

    def test_on_exception(self, playbook_app):
        """Test OnException decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # call method with decorator
        try:
            self.on_exception()
            assert False, 'exception not caught by decorator'
        except SystemExit as e:
            assert self.exit_message == 'on_exception method failed'
            assert e.code == 1

    @OnException(exit_msg='on_exception method no exit', exit_enabled='fail_on_error')
    def on_exception_exit_enabled_false(self):
        """Test fail on input decorator with no arg value (use first arg input)."""
        raise AttributeError()

    def test_on_exception_exit_enabled_false(self, playbook_app):
        """Test OnException decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'fail_on_error': False}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # call method with decorator
        self.on_exception_exit_enabled_false()
        assert self.exit_message == 'on_exception method no exit'

    def write_output(self):
        """Pass for coverage of write_output input."""

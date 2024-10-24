"""TcEx Framework Module"""

# standard library
import logging
from collections.abc import Callable

# first-party
from tcex.app.decorator.on_exception import OnException
from tests.mock_app import MockApp


class TestOnExceptionDecorators:
    """Test the TcEx Decorators."""

    args = None
    exit_message = None
    log = logging.getLogger('dummy')
    playbook = None
    tcex = None

    @OnException(
        exit_msg='on_exception method failed',
        exit_enabled='fail_on_error',
    )  # type: ignore
    def on_exception(self):
        """Test fail on input decorator with no arg value (use first arg input)."""
        raise AttributeError()

    def test_on_exception(self, playbook_app: Callable[..., MockApp]):
        """Test OnException decorator."""
        config_data = {'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.playbook = self.tcex.app.playbook

        # call method with decorator
        try:
            self.on_exception()
            assert False, 'exception not caught by decorator'
        except SystemExit as e:
            assert self.exit_message == 'on_exception method failed'
            assert e.code == 1

    @OnException(
        exit_msg='on_exception method no exit',
        exit_enabled='fail_on_error',
    )  # type: ignore
    def on_exception_exit_enabled_false(self):
        """Test fail on input decorator with no arg value (use first arg input)."""
        raise AttributeError()

    def test_on_exception_exit_enabled_false(self, playbook_app: Callable[..., MockApp]):
        """Test OnException decorator."""
        config_data = {'fail_on_error': False}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.playbook = self.tcex.app.playbook

        # call method with decorator
        self.on_exception_exit_enabled_false()
        assert self.exit_message == 'on_exception method no exit'

    def write_output(self):
        """Pass for coverage of write_output input."""

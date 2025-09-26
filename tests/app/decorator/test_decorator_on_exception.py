"""TestDecoratorOnException for TcEx App Decorator On Exception Module Testing.

This module contains comprehensive test cases for the TcEx App Decorator On Exception Module,
specifically testing the OnException decorator functionality including exception handling,
exit message setting, and proper decorator behavior across different exception
scenarios for graceful error handling in Apps.

Classes:
    TestDecoratorOnException: Test class for TcEx App Decorator On Exception Module functionality

TcEx Module Tested: app.decorator.on_exception
"""


import logging
from collections.abc import Callable
from typing import Any

import pytest


from tcex.app.decorator.on_exception import OnException
from tests.mock_app import MockApp


class TestDecoratorOnException:
    """TestDecoratorOnException for TcEx App Decorator On Exception Module Testing.

    This class provides comprehensive testing for the TcEx App Decorator On Exception Module,
    covering various on-exception scenarios including exception handling, exit message
    setting, and proper decorator behavior for graceful error handling in Apps.
    """

    args: Any = None
    exit_message: str | None = None
    log: logging.Logger = logging.getLogger('dummy')
    playbook: Any = None
    tcex: Any = None

    @OnException(
        exit_msg='on_exception method failed',
        exit_enabled='fail_on_error',
    )  # type: ignore
    def on_exception(self) -> None:
        """Test on exception decorator with exit enabled.

        This method is decorated with the OnException decorator to test its functionality
        for exception handling and exit message setting when exceptions occur.
        """
        raise AttributeError

    def test_on_exception(self, playbook_app: Callable[..., MockApp]) -> None:
        """Test On Exception Decorator for TcEx App Decorator On Exception Module.

        This test case verifies that the OnException decorator properly catches
        exceptions and sets appropriate exit messages when exit is enabled,
        ensuring the decorator correctly handles error scenarios with proper
        exit codes and message setting.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        config_data = {'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.playbook = self.tcex.app.playbook

        # call method with decorator
        with pytest.raises(SystemExit) as exc_info:
            self.on_exception()

        assert exc_info.value.code == 1, (
            f'exit code ({exc_info.value.code}) does not match expected (1)'
        )
        assert self.exit_message == 'on_exception method failed', (
            f'exit message ({self.exit_message}) does not match expected '
            f'(on_exception method failed)'
        )

    @OnException(
        exit_msg='on_exception method no exit',
        exit_enabled='fail_on_error',
    )  # type: ignore
    def on_exception_exit_enabled_false(self) -> None:
        """Test on exception decorator with exit disabled.

        This method is decorated with the OnException decorator to test its functionality
        for exception handling when exit is disabled, ensuring proper message setting
        without system exit.
        """
        raise AttributeError

    def test_on_exception_exit_enabled_false(
        self, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test On Exception Decorator Exit Disabled for TcEx App Decorator On Exception Module.

        This test case verifies that the OnException decorator properly handles
        exceptions without system exit when exit is disabled, ensuring the decorator
        correctly sets exit messages for graceful error handling without
        terminating the application.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        config_data = {'fail_on_error': False}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.playbook = self.tcex.app.playbook

        # call method with decorator
        self.on_exception_exit_enabled_false()
        assert self.exit_message == 'on_exception method no exit', (
            f'exit message ({self.exit_message}) does not match expected '
            f'(on_exception method no exit)'
        )

"""TestDecoratorOnSuccess for TcEx App Decorator On Success Module Testing.

This module contains comprehensive test cases for the TcEx App Decorator On Success Module,
specifically testing the OnSuccess decorator functionality including success message
setting, exit message configuration, and proper decorator behavior across different
success scenarios for App completion messaging.

Classes:
    TestDecoratorOnSuccess: Test class for TcEx App Decorator On Success Module functionality

TcEx Module Tested: app.decorator.on_success
"""


from collections.abc import Callable
from typing import Any


from tcex.app.decorator.on_success import OnSuccess
from tests.mock_app import MockApp


class TestDecoratorOnSuccess:
    """TestDecoratorOnSuccess for TcEx App Decorator On Success Module Testing.

    This class provides comprehensive testing for the TcEx App Decorator On Success Module,
    covering various on-success scenarios including success message setting, exit
    message configuration, and proper decorator behavior for App completion messaging.
    """

    args: Any = None
    exit_message: str | None = None
    tcex: Any = None

    @OnSuccess(exit_msg='on_success method passed')  # type: ignore
    def on_success(self) -> None:
        """Test on success decorator with custom exit message.

        This method is decorated with the OnSuccess decorator to test its functionality
        for setting exit messages on successful execution.
        """

    def test_on_success(self, playbook_app: Callable[..., MockApp]) -> None:
        """Test On Success Decorator for TcEx App Decorator On Success Module.

        This test case verifies that the OnSuccess decorator properly sets
        exit messages when methods complete successfully, ensuring the decorator
        correctly configures completion messaging for App success scenarios.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        self.tcex = playbook_app().tcex

        # call method with decorator
        self.on_success()
        assert self.exit_message == 'on_success method passed', (
            f'exit message ({self.exit_message}) does not match expected (on_success method passed)'
        )

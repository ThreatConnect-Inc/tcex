"""TestDecoratorFailOnOutput for TcEx App Decorator Fail On Output Module Testing.

This module contains comprehensive test cases for the TcEx App Decorator Fail On Output Module,
specifically testing the FailOnOutput decorator functionality including output validation,
conditional failure handling, and proper decorator behavior across different output
scenarios for controlling App execution based on return values.

Classes:
    TestDecoratorFailOnOutput: Test class for TcEx App Decorator Fail On Output Module functionality

TcEx Module Tested: app.decorator.fail_on_output
"""


from collections.abc import Callable
from typing import Any


import pytest


from tcex.app.decorator.fail_on_output import FailOnOutput
from tests.mock_app import MockApp


class TestDecoratorFailOnOutput:
    """TestDecoratorFailOnOutput for TcEx App Decorator Fail On Output Module Testing.

    This class provides comprehensive testing for the TcEx App Decorator Fail On Output Module,
    covering various fail-on-output scenarios including output validation, conditional
    failure handling, and proper decorator behavior for controlling App execution
    based on method return values.
    """

    args: Any = None
    exit_message: str | None = None
    fail_msg: str | None = None
    tcex: Any = None

    @FailOnOutput(
        fail_enabled='fail_on_error',
        fail_msg='Failed due to invalid output',
        fail_msg_property='fail_msg',
        fail_on=[None, ''],
    )  # type: ignore
    def fail_on_output(self, **kwargs: Any) -> Any:
        """Test fail on output decorator with keyword arguments.

        This method is decorated with the FailOnOutput decorator to test its functionality
        for output validation and conditional failure handling.
        """
        return kwargs.get('value')

    @pytest.mark.parametrize(
        'value',
        [
            pytest.param(None, id='fail-none-value'),
            pytest.param([None], id='fail-none-list'),
            pytest.param('', id='fail-empty-string'),
            pytest.param([''], id='fail-empty-string-list'),
        ],
    )
    def test_fail_on_output(
        self, value: Any, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Fail On Output Decorator Failure for TcEx App Decorator Fail On Output Module.

        This test case verifies that the FailOnOutput decorator properly fails
        when invalid output values are returned, ensuring the decorator correctly
        catches and handles invalid output scenarios with appropriate error messages
        and exit codes.

        Parameters:
            value: The invalid output value that should trigger failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        config_data = {'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.fail_msg = f'Failed due to invalid output {value}'

        # call decorated method and get result
        with pytest.raises(SystemExit) as exc_info:
            self.fail_on_output(value=value)

        assert exc_info.value.code == 1, (
            f'exit code ({exc_info.value.code}) does not match expected (1)'
        )
        # must match default value in decorator or value passed to decorator
        assert self.exit_message == self.fail_msg, (
            f'exit message ({self.exit_message}) does not match expected ({self.fail_msg})'
        )

    @pytest.mark.parametrize(
        'value',
        [pytest.param('good data', id='pass-valid-data')],
    )
    def test_fail_on_output_pass(
        self, value: str, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Fail On Output Decorator Pass for TcEx App Decorator Fail On Output Module.

        This test case verifies that the FailOnOutput decorator allows execution
        to continue when valid output values are returned, ensuring the decorator
        properly validates output and only fails when invalid conditions are met.

        Parameters:
            value: The valid output value that should not trigger failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        config_data = {'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex

        # call decorated method and get result
        result = self.fail_on_output(value=value)
        assert result == value, f'result of ({result}) does not match expected ({value})'

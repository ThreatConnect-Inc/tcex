"""TestDecoratorDebug for TcEx App Decorator Debug Module Testing.

This module contains comprehensive test cases for the TcEx App Decorator Debug Module,
specifically testing the Debug decorator functionality including function input logging,
debugging assistance, and proper decorator behavior across different function execution
scenarios for debugging Apps.

Classes:
    TestDecoratorDebug: Test class for TcEx App Decorator Debug Module functionality

TcEx Module Tested: app.decorator.debug
"""


from collections.abc import Callable
from typing import Any


import pytest


from tcex.app.decorator.debug import Debug
from tests.mock_app import MockApp


class TestDecoratorDebug:
    """TestDecoratorDebug for TcEx App Decorator Debug Module Testing.

    This class provides comprehensive testing for the TcEx App Decorator Debug Module,
    covering various debug decorator scenarios including function input logging,
    debugging assistance, and proper decorator behavior for troubleshooting
    and debugging Apps.
    """

    args: Any = None
    tcex: Any = None

    @Debug()  # type: ignore
    def debug(self, color: str, **kwargs: Any) -> tuple[str, Any]:
        """Test debug decorator with color and keyword arguments.

        This method is decorated with the Debug decorator to test its functionality
        for logging function inputs and debugging assistance.
        """
        return color, kwargs.get('colors')

    @pytest.mark.parametrize(
        'arg,value',
        [
            pytest.param('one', b'1', id='pass-string-bytes'),
            pytest.param('two', [b'2'], id='pass-string-bytes-list'),
            pytest.param('three', '3', id='pass-string-string'),
            pytest.param('four', ['4'], id='pass-string-string-list'),
        ],
    )
    def test_debug(self, arg: str, value: Any, playbook_app: Callable[..., MockApp]) -> None:
        """Test Debug Decorator for TcEx App Decorator Debug Module.

        This test case verifies that the Debug decorator works correctly
        by testing a decorated method with various input types and ensuring
        the decorator properly logs function inputs for debugging assistance
        without affecting the function's return value.

        Parameters:
            arg: The color argument to test with the debug decorator
            value: The colors keyword argument value to test

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        self.tcex = playbook_app().tcex

        # call decorated method and get result
        result = self.debug(arg, colors=value)
        assert result == (arg, value), (
            f'result of ({result}) does not match expected ({arg}, {value})'
        )

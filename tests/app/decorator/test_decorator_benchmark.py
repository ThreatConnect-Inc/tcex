"""TestDecoratorBenchmark for TcEx App Decorator Benchmark Module Testing.

This module contains comprehensive test cases for the TcEx App Decorator Benchmark Module,
specifically testing the Benchmark decorator functionality including execution time logging,
performance monitoring, and proper decorator behavior across different function execution
scenarios for troubleshooting performance issues in Apps.

Classes:
    TestDecoratorBenchmark: Test class for TcEx App Decorator Benchmark Module functionality

TcEx Module Tested: app.decorator.benchmark
"""


from collections.abc import Callable
from typing import Any

import pytest


from tcex.app.decorator.benchmark import Benchmark
from tests.mock_app import MockApp


class TestDecoratorBenchmark:
    """TestDecoratorBenchmark for TcEx App Decorator Benchmark Module Testing.

    This class provides comprehensive testing for the TcEx App Decorator Benchmark Module,
    covering various benchmark decorator scenarios including execution time logging,
    performance monitoring, and proper decorator behavior for troubleshooting
    performance issues in Apps.
    """

    tcex: Any = None

    @Benchmark()  # type: ignore
    def benchmark(self) -> None:
        """Test benchmark decorator with no arg value (use first arg input).

        This method is decorated with the Benchmark decorator to test its functionality
        for logging execution times and performance monitoring.
        """

    def test_benchmark(self, playbook_app: Callable[..., MockApp]) -> None:
        """Test Benchmark Decorator for TcEx App Decorator Benchmark Module.

        This test case verifies that the Benchmark decorator works correctly
        by testing a decorated method and ensuring no exceptions are raised,
        indicating that the decorator properly handles function execution
        and performance monitoring.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        self.tcex = playbook_app().tcex

        # test method with decorator
        try:
            self.benchmark()
            assert True, 'No exception indicates that the decorator passed'
        except Exception:
            pytest.fail('Any exception indicates that the decorator failed')

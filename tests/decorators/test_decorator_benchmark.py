# -*- coding: utf-8 -*-
"""Test the TcEx Benchmark Decorator."""
# first-party
from tcex import Benchmark


# pylint: disable=no-self-use
class TestBenchmarkDecorators:
    """Test the TcEx Decorators."""

    tcex = None

    @Benchmark()
    def benchmark(self):
        """Test fail on input decorator with no arg value (use first arg input)."""

    def test_benchmark(self, playbook_app):
        """Test Benchmark decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        self.tcex = playbook_app().tcex

        # test method with decorator
        try:
            self.benchmark()
            assert True, 'No exception indicates that the decorator passed'
        except Exception:
            assert False, 'Any exception indicates that the decorator failed'

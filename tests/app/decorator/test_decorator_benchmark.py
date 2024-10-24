"""TcEx Framework Module"""

# standard library
from collections.abc import Callable

# first-party
from tcex.app.decorator.benchmark import Benchmark
from tests.mock_app import MockApp


class TestBenchmarkDecorators:
    """Test the TcEx Decorators."""

    tcex = None

    @Benchmark()  # type: ignore
    def benchmark(self):
        """Test fail on input decorator with no arg value (use first arg input)."""

    def test_benchmark(self, playbook_app: Callable[..., MockApp]):
        """Test Benchmark decorator."""
        self.tcex = playbook_app().tcex

        # test method with decorator
        try:
            self.benchmark()
            assert True, 'No exception indicates that the decorator passed'
        except Exception:
            assert False, 'Any exception indicates that the decorator failed'

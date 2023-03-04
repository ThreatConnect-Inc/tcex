"""Test Module"""

# third-party
import pytest

# first-party
from tcex import TcEx


@pytest.mark.run(order=1)
class TestStreamHandler:
    """Test Module"""

    @staticmethod
    def test_stream_handler(tcex: TcEx):
        """Test Case"""
        handler_name = 'pytest-sh'
        tcex.logger.add_stream_handler(name=handler_name, level='trace')
        tcex.logger.remove_handler_by_name(handler_name)

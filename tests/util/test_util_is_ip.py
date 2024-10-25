"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.util import Util


class TestUtilIsIp:
    """Test Suite"""

    @pytest.mark.parametrize(
        'possible_ip,expected',
        [
            ('8.8.8.8', True),
            ('2001:0db8:0000:0000:0000:8a2e:0370:7334', True),
            ('foo bar', False),
        ],
    )
    def test_is_ip(self, possible_ip: str, expected: bool):
        """Test Case"""
        assert Util.is_ip(possible_ip) is expected

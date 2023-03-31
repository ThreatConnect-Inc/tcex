"""TcEx Framework Module"""
# third-party
import pytest

# first-party
from tcex.util import Util


class TestUtilIsCidr:
    """Test Suite"""

    @pytest.mark.parametrize(
        'possible_cidr_range,expected',
        [
            ('8.8.8.0/24', True),
            ('8.8.8.1/24', True),
            ('2001:db8::/128', True),
            ('8.8.8.8', False),
            ('foo bar', False),
        ],
    )
    def test_is_cidr(self, possible_cidr_range: str, expected: bool):
        """Test Case"""
        assert Util.is_cidr(possible_cidr_range) is expected

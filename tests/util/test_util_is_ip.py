"""TestUtilIsIp for testing IP address validation functionality.

Test suite for validating the Util.is_ip method functionality which determines
whether a given string represents a valid IP address (IPv4 or IPv6).

Classes:
    TestUtilIsIp: Test suite for IP address validation

TcEx Module Tested: tcex.util.Util
"""


import pytest


from tcex.util import Util


class TestUtilIsIp:
    """TestUtilIsIp for testing IP address validation functionality.

    Test suite for validating the Util.is_ip method which determines whether a given
    string represents a valid IP address (IPv4 or IPv6). Tests various valid and invalid
    IP address formats to ensure proper validation behavior.
    """

    @pytest.mark.parametrize(
        'possible_ip,expected',
        [
            pytest.param('8.8.8.8', True, id='pass-valid-ipv4'),  # valid IPv4
            pytest.param(
                '2001:0db8:0000:0000:0000:8a2e:0370:7334', True, id='pass-valid-ipv6'
            ),  # valid IPv6
            pytest.param('foo bar', False, id='pass-invalid-string'),  # invalid string
        ],
    )
    def test_is_ip(self, possible_ip: str, expected: bool):
        """Test Case for IP address validation functionality.

        Test that validates the Util.is_ip method correctly identifies valid and invalid
        IP addresses including IPv4, IPv6, and non-IP strings. Ensures proper boolean
        return values for various input formats.
        """
        assert Util.is_ip(possible_ip) is expected

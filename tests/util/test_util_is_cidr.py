"""TestUtilIsCidr for testing CIDR notation validation functionality.

Test suite for validating the Util.is_cidr method functionality which determines
whether a given string represents a valid CIDR notation (IPv4 or IPv6 network range).

Classes:
    TestUtilIsCidr: Test suite for CIDR notation validation

TcEx Module Tested: tcex.util.Util
"""


import pytest


from tcex.util import Util


class TestUtilIsCidr:
    """TestUtilIsCidr for testing CIDR notation validation functionality.

    Test suite for validating the Util.is_cidr method which determines whether a given
    string represents a valid CIDR notation (IPv4 or IPv6 network range). Tests various
    valid and invalid CIDR formats to ensure proper validation behavior.
    """

    @pytest.mark.parametrize(
        'possible_cidr_range,expected',
        [
            pytest.param('8.8.8.0/24', True, id='pass-valid-ipv4-cidr'),
            pytest.param('8.8.8.1/24', True, id='pass-valid-ipv4-cidr-host'),
            pytest.param('2001:db8::/128', True, id='pass-valid-ipv6-cidr'),
            pytest.param('8.8.8.8', False, id='pass-invalid-ip-without-mask'),
            pytest.param('foo bar', False, id='pass-invalid-string'),
        ],
    )
    def test_is_cidr(self, possible_cidr_range: str, expected: bool):
        """Test Case for CIDR notation validation functionality.

        Test that validates the Util.is_cidr method correctly identifies valid and invalid
        CIDR notation strings including IPv4, IPv6 network ranges, and non-CIDR strings.
        Ensures proper boolean return values for various input formats.
        """
        assert Util.is_cidr(possible_cidr_range) is expected

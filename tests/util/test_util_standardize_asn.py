"""TestUtilStandardizeAsn for testing ASN standardization utility functions.

This module contains comprehensive test cases for the Util.standardize_asn method,
which handles standardization of Autonomous System Number (ASN) strings to a consistent format.

Classes:
    TestUtilStandardizeAsn: Test suite for ASN standardization functionality

TcEx Module Tested: tcex.util
"""


import pytest


from tcex.util import Util


class TestUtilStandardizeAsn:
    """TestUtilStandardizeAsn for testing ASN standardization utility functions.

    This test class provides comprehensive test coverage for the Util.standardize_asn method,
    which normalizes various ASN string formats (AS1234, ASN1234, AS 1234, etc.) into a
    consistent ASN format.
    """

    @pytest.mark.parametrize(
        'asn,expected',
        [
            pytest.param('1234', 'ASN1234', id='pass-numeric-only-asn'),
            pytest.param('AS1234', 'ASN1234', id='pass-as-prefix-asn'),
            pytest.param('AS 1234', 'ASN1234', id='pass-as-prefix-with-space'),
            pytest.param('ASN1234', 'ASN1234', id='pass-asn-prefix-unchanged'),
            pytest.param('ASN 1234', 'ASN1234', id='pass-asn-prefix-with-space'),
            pytest.param('foo', 'foo', id='pass-non-asn-string-unchanged'),
        ],
    )
    def test_standardize_asn(self, asn: str, expected: str) -> None:
        """Test the standardize_asn method with various ASN input formats.

        This test validates the standardization of Autonomous System Number (ASN) strings
        to the consistent ASN format, handling various input patterns including numeric only,
        AS prefix, ASN prefix, and whitespace variations.
        """
        assert Util.standardize_asn(asn) == expected

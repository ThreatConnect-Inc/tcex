"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.util import Util


class TestUtilStandardizeAsn:
    """Test Suite"""

    @pytest.mark.parametrize(
        'asn,expected',
        [
            ('1234', 'ASN1234'),
            ('AS1234', 'ASN1234'),
            ('AS 1234', 'ASN1234'),
            ('ASN1234', 'ASN1234'),
            ('ASN 1234', 'ASN1234'),
            ('foo', 'foo'),
        ],
    )
    def test_standardize_asn(self, asn: str, expected: str):
        """Test Case"""
        assert Util.standardize_asn(asn) == expected

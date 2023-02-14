"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestStandardizeAsn:
    """Test the TcEx Utils Module."""

    def test_standardize_asn(self):
        """Test Case"""
        assert Utils().standardize_asn('1234') == 'ASN1234'
        assert Utils().standardize_asn('AS1234') == 'ASN1234'
        assert Utils().standardize_asn('AS 1234') == 'ASN1234'
        assert Utils().standardize_asn('ASN1234') == 'ASN1234'
        assert Utils().standardize_asn('ASN 1234') == 'ASN1234'
        assert Utils().standardize_asn('foo') == 'foo'

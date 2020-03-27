# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class TestStandardizeAsn:
    """Test the TcEx Utils Module."""

    def test_standardize_asn(self, tcex):
        """Test an IPv4 CIDR range

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        assert tcex.utils.standardize_asn('1234') == 'ASN1234'
        assert tcex.utils.standardize_asn('AS1234') == 'ASN1234'
        assert tcex.utils.standardize_asn('AS 1234') == 'ASN1234'
        assert tcex.utils.standardize_asn('ASN1234') == 'ASN1234'
        assert tcex.utils.standardize_asn('ASN 1234') == 'ASN1234'
        assert tcex.utils.standardize_asn('foo') == 'foo'

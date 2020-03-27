# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class TestIsCidr:
    """Test the TcEx Utils Module."""

    def test_ipv4_cidr(self, tcex):
        """Test an IPv4 CIDR range

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = '8.8.8.0/24'
        assert tcex.utils.is_cidr(s)

    def test_ipv4_cidr_host_bits_set(self, tcex):
        """Test an IPv4 CIDR range with the host bits set.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = '8.8.8.1/24'
        assert tcex.utils.is_cidr(s)

    def test_ipv6_cidr(self, tcex):
        """Test an IPv6 CIDR range

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = '2001:db8::/128'
        assert tcex.utils.is_cidr(s)

    def test_invalid_ip_not_cidr(self, tcex):
        """Test a string that is not a CIDR range

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = '8.8.8.8'
        assert not tcex.utils.is_cidr(s)

    def test_invalid(self, tcex):
        """Test a string that is not a CIDR range

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = 'foo bar'
        assert not tcex.utils.is_cidr(s)

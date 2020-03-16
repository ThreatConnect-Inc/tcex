# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class TestIsIp:
    """Test the TcEx Utils Module."""

    def test_ipv4(self, tcex):
        """Test an IPv4 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = '8.8.8.8'
        assert tcex.utils.is_ip(s)

    def test_ipv6(self, tcex):
        """Test an IPv6 address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = '2001:0db8:0000:0000:0000:8a2e:0370:7334'
        assert tcex.utils.is_ip(s)

    def test_invalid(self, tcex):
        """Test a string that is not an IP address

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = 'foo bar'
        assert not tcex.utils.is_ip(s)

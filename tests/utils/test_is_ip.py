"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestIsIp:
    """Test the TcEx Utils Module."""

    @staticmethod
    def test_ipv4():
        """Test an IPv4 address."""
        s = '8.8.8.8'
        assert Utils().is_ip(s)

    @staticmethod
    def test_ipv6():
        """Test an IPv6 address."""
        s = '2001:0db8:0000:0000:0000:8a2e:0370:7334'
        assert Utils().is_ip(s)

    @staticmethod
    def test_invalid():
        """Test a string that is not an IP address."""
        s = 'foo bar'
        assert not Utils().is_ip(s)

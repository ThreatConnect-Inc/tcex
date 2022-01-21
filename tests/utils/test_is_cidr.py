"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestIsCidr:
    """Test the TcEx Utils Module."""

    @staticmethod
    def test_ipv4_cidr():
        """Test an IPv4 CIDR range."""
        s = '8.8.8.0/24'
        assert Utils().is_cidr(s)

    @staticmethod
    def test_ipv4_cidr_host_bits_set():
        """Test an IPv4 CIDR range with the host bits set."""
        s = '8.8.8.1/24'
        assert Utils().is_cidr(s)

    @staticmethod
    def test_ipv6_cidr():
        """Test an IPv6 CIDR range."""
        s = '2001:db8::/128'
        assert Utils().is_cidr(s)

    @staticmethod
    def test_invalid_ip_not_cidr():
        """Test a string that is not a CIDR range."""
        s = '8.8.8.8'
        assert not Utils().is_cidr(s)

    @staticmethod
    def test_invalid():
        """Test a string that is not a CIDR range."""
        s = 'foo bar'
        assert not Utils().is_cidr(s)

# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class TestIsCidr:
    """Test the TcEx Utils Module."""

    def test_shorten_group_name_1(self, tcex):
        """."""
        s = 'foo'
        assert tcex.utils.shorten_group_name(s) == s

        s = 'a'*100
        assert tcex.utils.shorten_group_name(s) == s

    def test_shorten_group_name_2(self, tcex):
        """."""
        s = 'a'*101
        assert tcex.utils.shorten_group_name(s) == f'{"a"*97}...'

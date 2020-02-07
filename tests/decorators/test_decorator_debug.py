# -*- coding: utf-8 -*-
"""Test the TcEx Debug Decorator."""
import pytest
from tcex import Debug


# pylint: disable=no-self-use
class TestIterateOnArgDecorators:
    """Test the TcEx Decorators."""

    args = None
    tcex = None

    @Debug()
    def debug(self, color, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return color, kwargs.get('colors')

    @pytest.mark.parametrize(
        'arg,value', [('one', b'1'), ('two', [b'2']), ('three', '3'), ('four', ['4'])],
    )
    def test_debug(self, arg, value, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        self.tcex = playbook_app().tcex

        # call decorated method and get result
        result = self.debug(arg, colors=value)
        assert result == (arg, value)

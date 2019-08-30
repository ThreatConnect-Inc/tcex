# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest
from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestBool:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'string,result',
        [
            ('true', True),
            ('1', True),
            (1, True),
            (True, True),
            ('false', False),
            ('0', False),
            (0, False),
            (False, False),
        ],
    )
    def test_bool(self, string, result):
        """Test any to datetime"""
        boolean_results = tcex.utils.to_bool(string)
        assert boolean_results == result, 'Boolean {} != {}'.format(boolean_results, result)

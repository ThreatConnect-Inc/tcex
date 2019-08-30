# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest
from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestInflect:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @pytest.mark.parametrize(
        'string,result',
        [
            # ('Adversary', 'Adversaries'),
            ('adversary', 'adversaries'),
            ('Campaign', 'Campaigns'),
            ('Document', 'Documents'),
            ('Email', 'Emails'),
            ('Event', 'Events'),
            ('Incident', 'Incidents'),
            ('Intrusion Set', 'Intrusion Sets'),
            ('Report', 'Reports'),
            ('Signature', 'Signatures'),
            ('Task', 'Tasks'),
            ('Threat', 'Threats'),
        ],
    )
    def test_inflect(self, string, result):
        """Test any to datetime"""
        plural_string = tcex.utils.inflect.plural(string)
        assert plural_string == result, 'String {} != {}'.format(plural_string, result)

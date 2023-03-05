"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils.string_operations import StringOperations


class TestStringOperationsInflect:
    """Test Suite"""

    so = StringOperations()

    @pytest.mark.parametrize(
        'string,expected',
        [
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
    def test_utils_inflect(self, string: str, expected: str):
        """Test Case"""
        result = self.so.inflect.plural(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

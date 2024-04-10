"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.util.string_operation import StringOperation


class TestStringOperationInflect:
    """Test Suite"""

    so = StringOperation()

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
        result = self.so.inflection.pluralize(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

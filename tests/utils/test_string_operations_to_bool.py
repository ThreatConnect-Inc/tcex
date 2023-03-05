"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils.string_operations import StringOperations


class TestStringOperationsToBool:
    """Test Suite"""

    so = StringOperations()

    @pytest.mark.parametrize(
        'string,expected',
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
    def test_string_operations_to_bool(self, string: str, expected: str):
        """Test Case"""
        result = self.so.to_bool(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

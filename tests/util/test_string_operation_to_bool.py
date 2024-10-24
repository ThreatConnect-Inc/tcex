"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.util.string_operation import StringOperation


class TestStringOperationToBool:
    """Test Suite"""

    so = StringOperation()

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
    def test_string_operation_to_bool(self, string: str, expected: str):
        """Test Case"""
        result = self.so.to_bool(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

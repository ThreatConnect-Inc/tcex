"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils.string_operations import StringOperations


class TestStringOperationsTruncateString:
    """Test Suite"""

    so = StringOperations()

    @pytest.mark.parametrize(
        'string,length,append_chars,spaces,expected',
        [
            # no truncate, no append, no spaces
            ('short_no_truncate', 20, '', False, 'short_no_truncate'),
            # no truncate, append, no spaces
            ('short_no_truncate', 20, ' ...', False, 'short_no_truncate'),
            # no truncate, append, spaces
            ('short_no_truncate', 20, '', True, 'short_no_truncate'),
            # truncate, no append, no spaces
            ('truncate_string', 5, '', False, 'trunc'),
            # truncate, append, no spaces
            ('truncate_append', 5, ' .', False, 'tru .'),
            # truncate, append, spaces
            ('truncate append spaces', 20, ' .', True, 'truncate append .'),
            # truncate, append, spaces
            ('truncate  double spaces', 20, ' .', True, 'truncate  double .'),
            # return input
            (None, 20, None, False, ''),
            # return input
            ('', 20, None, False, ''),
            # return input
            ('input', None, None, False, 'input'),
            # return input
            ('input', 100, None, False, 'input'),
            # return empty string
            ('input', 0, None, False, ''),
            # return empty string, spaces
            ('input', 2, None, True, ''),
        ],
    )
    def test_string_operations_truncate_string(
        self, string: str, length: int, append_chars: str | None, spaces: bool, expected: str
    ):
        """Test Case"""
        result = self.so.truncate_string(string, length, append_chars, spaces)
        assert result == expected, f'Input {string} result of {result} != {expected}'

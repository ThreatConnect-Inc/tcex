"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tcex.util.string_operation import StringOperation


class TestStringOperationTruncateString:
    """Test Suite"""

    so = StringOperation()

    @pytest.mark.parametrize(
        'string,length,append_chars,spaces,expected',
        [
            # no truncate, no append, no spaces
            ('short_no_truncate', 20, '', False, 'short_no_truncate'),
            # no truncate, append, no spaces
            ('short_no_truncate', 20, ' ...', False, 'short_no_truncate'),
            # no truncate, append, spaces
            ('short_no_truncate', 20, '', True, 'short_no_truncate'),
            # APP-4520
            ('this_is_a_longer_string_with_no_spaces', 10, '', True, 'this_is_a_'),
            # APP-4520
            ('this_is_a_longer_string_with_no_spaces', 10, '...', True, 'this_is...'),
            # APP-4520
            ('this_is_a_longer_string_with_no_spaces', 10, ' ...', True, 'this_i ...'),
            # APP-4520
            ('this_is_a_longer_string_with_no_spaces with spaces', 10, ' ...', True, 'this_i ...'),
            # APP-4520
            ('this_is_a longer_string_with_no_spaces with spaces', 10, '', True, 'this_is_a'),
            # APP-4520
            ('this_is_a longer_string_with_no_spaces with spaces', 10, '', False, 'this_is_a'),
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
            ('input', 2, None, True, 'in'),
        ],
    )
    def test_string_operation_truncate_string(
        self, string: str, length: int, append_chars: str | None, spaces: bool, expected: str
    ):
        """Test Case"""
        result = self.so.truncate_string(string, length, append_chars, spaces)
        assert result == expected, f'Input {string} result of {result} != {expected}'

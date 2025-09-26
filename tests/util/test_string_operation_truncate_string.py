"""TestStringOperationTruncateString for testing string truncation functionality.

Test cases for the StringOperation.truncate_string method covering various scenarios including
truncation, appending characters, space handling, and edge cases.

Classes:
    TestStringOperationTruncateString: Test suite for string truncation operations

TcEx Module Tested: tcex.util.string_operation
"""


import pytest


from tcex.util.string_operation import StringOperation


class TestStringOperationTruncateString:
    """TestStringOperationTruncateString for testing string truncation functionality.

    Test suite for the StringOperation.truncate_string method covering various scenarios
    including truncation, appending characters, space handling, and edge cases.
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'string,length,append_chars,spaces,expected',
        [
            # no truncate, no append, no spaces
            pytest.param(
                'short_no_truncate',
                20,
                '',
                False,
                'short_no_truncate',
                id='pass-no-truncate-no-append-no-spaces',
            ),
            # no truncate, append, no spaces
            pytest.param(
                'short_no_truncate',
                20,
                ' ...',
                False,
                'short_no_truncate',
                id='pass-no-truncate-append-no-spaces',
            ),
            # no truncate, append, spaces
            pytest.param(
                'short_no_truncate',
                20,
                '',
                True,
                'short_no_truncate',
                id='pass-no-truncate-append-spaces',
            ),
            # APP-4520
            pytest.param(
                'this_is_a_longer_string_with_no_spaces',
                10,
                '',
                True,
                'this_is_a_',
                id='pass-longer-string-no-append-spaces',
            ),
            # APP-4520
            pytest.param(
                'this_is_a_longer_string_with_no_spaces',
                10,
                '...',
                True,
                'this_is...',
                id='pass-longer-string-append-spaces',
            ),
            # APP-4520
            pytest.param(
                'this_is_a_longer_string_with_no_spaces',
                10,
                ' ...',
                True,
                'this_i ...',
                id='pass-longer-string-append-chars-spaces',
            ),
            # APP-4520
            pytest.param(
                'this_is_a_longer_string_with_no_spaces with spaces',
                10,
                ' ...',
                True,
                'this_i ...',
                id='pass-longer-string-with-spaces-append-chars-spaces',
            ),
            # APP-4520
            pytest.param(
                'this_is_a longer_string_with_no_spaces with spaces',
                10,
                '',
                True,
                'this_is_a',
                id='pass-longer-string-with-spaces-no-append-spaces',
            ),
            # APP-4520
            pytest.param(
                'this_is_a longer_string_with_no_spaces with spaces',
                10,
                '',
                False,
                'this_is_a',
                id='pass-longer-string-with-spaces-no-append-no-spaces',
            ),
            # truncate, no append, no spaces
            pytest.param(
                'truncate_string', 5, '', False, 'trunc', id='pass-truncate-no-append-no-spaces'
            ),
            # truncate, append, no spaces
            pytest.param(
                'truncate_append', 5, ' .', False, 'tru .', id='pass-truncate-append-no-spaces'
            ),
            # truncate, append, spaces
            pytest.param(
                'truncate append spaces',
                20,
                ' .',
                True,
                'truncate append .',
                id='pass-truncate-append-spaces',
            ),
            # truncate, append, spaces
            pytest.param(
                'truncate  double spaces',
                20,
                ' .',
                True,
                'truncate  double .',
                id='pass-truncate-append-double-spaces',
            ),
            # return input
            pytest.param(None, 20, None, False, '', id='pass-none-input'),
            # return input
            pytest.param('', 20, None, False, '', id='pass-empty-input'),
            # return input
            pytest.param('input', None, None, False, 'input', id='pass-none-length'),
            # return input
            pytest.param('input', 100, None, False, 'input', id='pass-long-length'),
            # return empty string
            pytest.param('input', 0, None, False, '', id='pass-zero-length'),
            # return empty string, spaces
            pytest.param('input', 2, None, True, 'in', id='pass-short-length-spaces'),
        ],
    )
    def test_string_operation_truncate_string(
        self, string: str, length: int, append_chars: str | None, spaces: bool, expected: str
    ):
        """Test String Operation Truncate String for various input scenarios.

        Tests the truncate_string method with different combinations of input parameters
        including normal truncation, appending characters, space handling, and edge cases.

        Parameters:
            string: Input string to truncate
            length: Maximum length for truncation
            append_chars: Characters to append after truncation
            spaces: Whether to preserve spaces during truncation
            expected: Expected result after truncation
        """
        result = self.so.truncate_string(string, length, append_chars, spaces)
        assert result == expected, f'Input {string} result of {result} != {expected}'

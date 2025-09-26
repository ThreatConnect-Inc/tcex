"""TestStringOperationWrapString for testing StringOperation.wrap_string method.

Tests the functionality of wrapping strings at specified character positions with configurable
wrap characters, length limits, and force wrap options to ensure proper text formatting.

Classes:
    TestStringOperationWrapString: Test suite for StringOperation.wrap_string method

TcEx Module Tested: tcex.util.string_operation
"""


import pytest


from tcex.util.string_operation import StringOperation


class TestStringOperationWrapString:
    """TestStringOperationWrapString for testing StringOperation.wrap_string method.

    Test suite that validates the functionality of wrapping strings at specified character
    positions with configurable wrap characters, length limits, and force wrap options to
    ensure proper text formatting.
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'line,wrap_chars,length,force_wrap,expected',
        [
            pytest.param(
                (
                    '# v1: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset'
                    '|Is Superset|Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase'
                    '|Symmetric Difference|Unique|Union'
                ),
                [' ', '|'],
                100,
                True,
                (
                    '# v1: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset'
                    '|Is Superset|Length|Pop|Reverse|\nReverse Sort|Slice|Sort|Sort Lowercase'
                    '|Symmetric Difference|Unique|Union'
                ),
                id='pass-wrap-with-space-and-pipe-force-true',
            ),
            pytest.param(
                (
                    '# v2: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset'
                    '|Is Superset|Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase'
                    '|Symmetric Difference|Unique|Union'
                ),
                [','],
                100,
                False,
                (
                    '# v2: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset'
                    '|Is Superset|Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase'
                    '|Symmetric Difference|Unique|Union'
                ),
                id='pass-wrap-with-comma-no-force-no-wrap',
            ),
            pytest.param(
                (
                    '# v3: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset'
                    '|Is Superset|Length|Pop|Reverse|Reverse Sort|Slice|Sort|Sort Lowercase'
                    '|Symmetric Difference|Unique|Union'
                ),
                [','],
                100,
                True,
                (
                    '# v3: Build|Difference|Duplicates|Fill|Intersection|Is In|Is Subset'
                    '|Is Superset|Length|Pop|Reverse|R\neverse Sort|Slice|Sort|Sort Lowercase'
                    '|Symmetric Difference|Unique|Union'
                ),
                id='pass-wrap-with-comma-force-true-mid-word',
            ),
            pytest.param(
                '',
                None,
                100,
                True,
                '',
                id='pass-empty-string-returns-empty',
            ),
            pytest.param(
                'foobar',
                None,
                100,
                True,
                'foobar',
                id='pass-short-string-no-wrap-chars-unchanged',
            ),
        ],
    )
    def test_string_operation_wrap_string(
        self,
        line: str,
        wrap_chars: list[str] | None,
        length: int,
        force_wrap: bool,
        expected: str,
    ) -> None:
        """Test String Operation Wrap String for validating StringOperation.wrap_string method.

        Tests the ability to wrap strings at specified character positions with configurable
        wrap characters, length limits, and force wrap options. Validates proper text formatting
        including edge cases with empty strings, None wrap characters, and various wrapping
        scenarios.
        """
        answer = self.so.wrap_string(line, wrap_chars, length, force_wrap)
        assert answer == expected, f'answer: {answer} expected: {expected}'

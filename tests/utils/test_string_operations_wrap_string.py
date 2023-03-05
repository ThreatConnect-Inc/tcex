"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils.string_operations import StringOperations


class TestStringOperationsWrapString:
    """Test Suite"""

    so = StringOperations()

    @pytest.mark.parametrize(
        'line,wrap_chars,length,force_wrap,expected',
        [
            (
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
            ),
            (
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
            ),
            (
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
            ),
            (
                '',
                None,
                100,
                True,
                '',
            ),
            (
                'foobar',
                None,
                100,
                True,
                'foobar',
            ),
        ],
    )
    def test_string_operations_wrap_string(
        self,
        line: str,
        wrap_chars: list[str] | None,
        length: int,
        force_wrap: bool,
        expected: str,
    ):
        """Test Case"""
        answer = self.so.wrap_string(line, wrap_chars, length, force_wrap)
        assert answer == expected, f'answer: {answer} expected: {expected}'

"""TestUtilFindLineInCode for testing CodeOperation.find_line_in_code method.

Tests the functionality of finding specific lines of code within a code block using pattern
matching with configurable start and stop triggers.

Classes:
    TestUtilFindLineInCode: Test suite for CodeOperation.find_line_in_code method

TcEx Module Tested: tcex.util.code_operation
"""


from pathlib import Path
from re import Pattern


import pytest

from _pytest.fixtures import FixtureRequest


from tcex.util.code_operation import CodeOperation


class TestUtilFindLineInCode:
    """TestUtilFindLineInCode for testing CodeOperation.find_line_in_code method.

    Test suite that validates the functionality of finding specific lines of code within a code
    block using pattern matching with configurable start and stop triggers.
    """

    @pytest.mark.parametrize(
        'needle,trigger_start,trigger_stop,expected',
        [
            pytest.param(
                '.*code\\s=.*',
                '.*test_util_find_line_in_code.*',
                '.*result == expected.*',
                'code = fh.read()',
                id='pass-find-code-line-between-triggers',
            ),
            pytest.param(
                'do_not_find_this',
                '.*test_util_find_line_in_code.*',
                '.*result == expected.*',
                None,
                id='pass-no-match-returns-none',
            ),
        ],
    )
    def test_util_find_line_in_code(
        self,
        needle: str,
        trigger_start: str | Pattern,
        trigger_stop: str | Pattern,
        expected: list,
        request: FixtureRequest,
    ) -> None:
        """Test Util Find Line In Code for validating CodeOperation.find_line_in_code method.

        Tests the ability to find specific lines of code within a code block using pattern matching
        with configurable start and stop triggers, ensuring proper handling of both successful
        matches and cases where no match is found.

        Fixtures:
            request: Pytest fixture providing information about the requesting test function
        """
        filename = Path(request.fspath.dirname) / 'test_util_find_line_in_code.py'  # type: ignore
        with filename.open() as fh:
            code = fh.read()

        result = CodeOperation.find_line_in_code(needle, code, trigger_start, trigger_stop)
        assert result == expected, f"Expected {expected} but got {result} for needle '{needle}'"

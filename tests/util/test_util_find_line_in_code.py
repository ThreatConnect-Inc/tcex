"""TcEx Framework Module"""
# standard library
from pathlib import Path
from re import Pattern

# third-party
import pytest
from _pytest.fixtures import FixtureRequest

# first-party
from tcex.util.code_operation import CodeOperation


class TestUtilFindLineInCode:
    """Test Suite"""

    @pytest.mark.parametrize(
        'needle,trigger_start,trigger_stop,expected',
        [
            (
                '.*code.*',
                '.*test_util_find_line_in_code.*',
                '.*result == expected.*',
                'code = fh.read()',
            ),
            (
                'do_not_find_this',
                '.*test_util_find_line_in_code.*',
                '.*result == expected.*',
                None,
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
    ):
        """Test Case"""
        filename = Path(request.fspath.dirname) / 'test_util_find_line_in_code.py'  # type: ignore
        with open(filename) as fh:
            code = fh.read()

        result = CodeOperation.find_line_in_code(needle, code, trigger_start, trigger_stop)
        print(result)
        assert result == expected

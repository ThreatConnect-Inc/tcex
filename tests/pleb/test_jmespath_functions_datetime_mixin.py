"""Tests for tcex.pleb.jmespath_functions_datetime_mixin (DateTimeFunctionsMixin)."""

# standard library
import re
from typing import Any

# third-party
import jmespath
import pytest

# first-party
from tcex.pleb.jmespath_custom import jmespath_options


def _search(expr: str, data: Any) -> Any:
    """Evaluate a JMESPath expression with TcFunctions custom functions."""
    return jmespath.search(expr, data, options=jmespath_options())


class TestDateTimeFunctionsMixin:
    """Tests for datetime JMESPath functions."""

    # datetime_format
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                "datetime_format(ts, '%Y-%m-%dT%H:%M:%SZ')",
                {'ts': '2024-01-15 08:30:00'},
                '2024-01-15T08:30:00Z',
                id='pass-iso-string-reformatted',
            ),
            pytest.param(
                "datetime_format(ts, '%Y-%m-%dT%H:%M:%SZ')",
                {'ts': 1705307400000},
                '2024-01-15T08:30:00Z',
                id='pass-epoch-ms-to-string',
            ),
            pytest.param(
                "datetime_format(ts, '%Y-%m-%d')",
                {'ts': '2024-01-15T08:30:00Z'},
                '2024-01-15',
                id='pass-date-only-output',
            ),
            pytest.param(
                "datetime_format(ts, '%H:%M')",
                {'ts': '2024-01-15T08:30:00Z'},
                '08:30',
                id='pass-time-only-output',
            ),
        ],
    )
    def test_datetime_format(self, expr: str, data: dict, expected: str) -> None:
        assert _search(expr, data) == expected

    # datetime_now
    def test_datetime_now_returns_integer(self) -> None:
        assert isinstance(_search('datetime_now()', {}), int)

    def test_datetime_now_is_recent_epoch_ms(self) -> None:
        assert _search('datetime_now()', {}) > 1_700_000_000_000

    # datetime_now_utc
    def test_datetime_now_utc_returns_rfc3339(self) -> None:
        result = _search('datetime_now_utc()', {})
        assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', result)

    # datetime_to_epoch
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'datetime_to_epoch(ts)',
                {'ts': '2024-01-15T08:30:00Z'},
                1705307400000,
                id='pass-iso-string-to-epoch-ms',
            ),
            pytest.param(
                'datetime_to_epoch(ts)',
                {'ts': '2024-01-15 08:30:00'},
                1705307400000,
                id='pass-naive-string-to-epoch-ms',
            ),
            pytest.param(
                'datetime_to_epoch(ts)',
                {'ts': 1705307400000},
                1705307400000,
                id='pass-epoch-ms-round-trip',
            ),
        ],
    )
    def test_datetime_to_epoch(self, expr: str, data: dict, expected: int) -> None:
        assert _search(expr, data) == expected

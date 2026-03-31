"""Tests for tcex.pleb.jmespath_functions_control_mixin (ControlFunctionsMixin)."""

# standard library
from typing import Any

# third-party
import jmespath
import pytest

# first-party
from tcex.pleb.jmespath_custom import jmespath_options


def _search(expr: str, data: Any) -> Any:
    """Evaluate a JMESPath expression with TcFunctions custom functions."""
    return jmespath.search(expr, data, options=jmespath_options())


class TestControlFunctionsMixin:
    """Tests for control flow JMESPath functions."""

    # has_value
    @pytest.mark.parametrize(
        'value,expected',
        [
            pytest.param('active', True, id='pass-non-empty-string-is-truthy'),
            pytest.param('', False, id='pass-empty-string-is-falsy'),
            pytest.param(42, True, id='pass-non-zero-number-is-truthy'),
            pytest.param(0, False, id='pass-zero-is-falsy'),
            pytest.param(True, True, id='pass-bool-true-is-truthy'),
            pytest.param(False, False, id='pass-bool-false-is-falsy'),
            pytest.param(None, False, id='pass-null-is-falsy'),
        ],
    )
    def test_has_value(self, value: Any, expected: bool) -> None:
        assert _search('has_value(v)', {'v': value}) is expected

    # in
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'in(status, statuses)',
                {'status': 'active', 'statuses': ['active', 'pending']},
                True,
                id='pass-element-present',
            ),
            pytest.param(
                'in(status, statuses)',
                {'status': 'closed', 'statuses': ['active', 'pending']},
                False,
                id='pass-element-absent',
            ),
            pytest.param(
                'in(severity, alert.allowed_severities)',
                {'severity': 'HIGH', 'alert': {'allowed_severities': ['HIGH', 'CRITICAL']}},
                True,
                id='pass-nested-array-element-present',
            ),
            pytest.param(
                'in(severity, alert.allowed_severities)',
                {'severity': 'LOW', 'alert': {'allowed_severities': ['HIGH', 'CRITICAL']}},
                False,
                id='pass-nested-array-element-absent',
            ),
        ],
    )
    def test_in(self, expr: str, data: dict, expected: bool) -> None:
        assert _search(expr, data) is expected

    # ternary
    @pytest.mark.parametrize(
        'condition,data,expected',
        [
            pytest.param(
                "contains(tags, 'critical')",
                {'tags': ['critical']},
                'HIGH',
                id='pass-contains-truthy-returns-if-true',
            ),
            pytest.param(
                "contains(tags, 'critical')",
                {'tags': ['info']},
                'LOW',
                id='pass-contains-falsy-returns-if-false',
            ),
            pytest.param(
                'has_value(condition)',
                {'condition': 'active'},
                'HIGH',
                id='pass-has-value-truthy-returns-if-true',
            ),
            pytest.param(
                'has_value(condition)',
                {'condition': ''},
                'LOW',
                id='pass-has-value-empty-string-returns-if-false',
            ),
            pytest.param(
                'has_value(condition)',
                {'condition': False},
                'LOW',
                id='pass-has-value-bool-false-returns-if-false',
            ),
            pytest.param(
                'has_value(condition)',
                {'condition': None},
                'LOW',
                id='pass-has-value-null-returns-if-false',
            ),
        ],
    )
    def test_ternary(self, condition: str, data: dict, expected: str) -> None:
        assert _search(f"ternary({condition}, 'HIGH', 'LOW')", data) == expected

    # type
    @pytest.mark.parametrize(
        'value,expected',
        [
            pytest.param([1], 'ARRAY', id='pass-array'),
            pytest.param({'k': 1}, 'OBJECT', id='pass-object'),
            pytest.param('hello', 'STRING', id='pass-string'),
            pytest.param(42, 'NUMBER', id='pass-number'),
            pytest.param(True, 'BOOLEAN', id='pass-boolean'),
            pytest.param(None, 'NULL', id='pass-null'),
        ],
    )
    def test_type(self, value: Any, expected: str) -> None:
        assert _search('type(v)', {'v': value}) == expected

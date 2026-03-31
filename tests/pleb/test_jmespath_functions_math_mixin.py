"""Tests for tcex.pleb.jmespath_functions_math_mixin (MathFunctionsMixin)."""

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


class TestMathFunctionsMixin:
    """Tests for math JMESPath functions."""

    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'add(a, b)',
                {'a': 9.99, 'b': 0.01},
                pytest.approx(10.0),
                id='pass-two-floats',
            ),
            pytest.param(
                'add(a, b)',
                {'a': 3, 'b': 4},
                7,
                id='pass-two-integers',
            ),
            pytest.param(
                'add(a, b, c)',
                {'a': 1, 'b': 2, 'c': 3},
                6,
                id='pass-three-values',
            ),
            pytest.param(
                'add(amounts)',
                {'amounts': [1, 2, 3]},
                6,
                id='pass-array-reference',
            ),
        ],
    )
    def test_add(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'divide(a, b)',
                {'a': 10.0, 'b': 4.0},
                pytest.approx(2.5),
                id='pass-returns-quotient',
            ),
            pytest.param(
                'divide(a, b)',
                {'a': 10.0, 'b': 0.0},
                None,
                id='pass-divide-by-zero-returns-null',
            ),
        ],
    )
    def test_divide(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param('mod(a, b)', {'a': 7, 'b': 3}, 1, id='pass-remainder'),
            pytest.param('mod(a, b)', {'a': 9, 'b': 3}, 0, id='pass-exact-divisor'),
        ],
    )
    def test_mod(self, expr: str, data: dict, expected: int) -> None:
        assert _search(expr, data) == expected

    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'multiply(a, b)', {'a': 3.0, 'b': 4.0}, pytest.approx(12.0), id='pass-two-floats'
            ),
            pytest.param('multiply(a, b, c)', {'a': 2, 'b': 3, 'c': 4}, 24, id='pass-three-values'),
            pytest.param(
                'multiply(factors)', {'factors': [2, 3, 4]}, 24, id='pass-array-reference'
            ),
        ],
    )
    def test_multiply(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param('power(a, b)', {'a': 2, 'b': 3}, 8, id='pass-exponentiation'),
            pytest.param('power(a, b)', {'a': 5, 'b': 0}, 1, id='pass-zero-exponent'),
        ],
    )
    def test_power(self, expr: str, data: dict, expected: int) -> None:
        assert _search(expr, data) == expected

    def test_rand_int_within_range(self) -> None:
        result = _search('rand_int(mn, mx)', {'mn': 1, 'mx': 100})
        assert 1 <= result <= 100

    def test_rand_int_returns_integer(self) -> None:
        assert isinstance(_search('rand_int(mn, mx)', {'mn': 1, 'mx': 10}), int)

    def test_rand_int_same_min_max(self) -> None:
        assert _search('rand_int(mn, mx)', {'mn': 5, 'mx': 5}) == 5

    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param('subtract(a, b)', {'a': 100, 'b': 15}, 85, id='pass-two-values'),
            pytest.param(
                'subtract(a, b, c)', {'a': 100, 'b': 15, 'c': 5}, 80, id='pass-three-values'
            ),
            pytest.param(
                'subtract(amounts)', {'amounts': [100, 15, 5]}, 80, id='pass-array-reference'
            ),
        ],
    )
    def test_subtract(self, expr: str, data: dict, expected: int) -> None:
        assert _search(expr, data) == expected

    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param('to_int(v)', {'v': 9.9}, 9, id='pass-truncates-float'),
            pytest.param('to_int(v)', {'v': -3.7}, -3, id='pass-negative-truncates-toward-zero'),
            pytest.param('to_int(v)', {'v': 5}, 5, id='pass-integer-unchanged'),
            pytest.param('to_int(a, b)', {'a': 9.9, 'b': -3.7}, [9, -3], id='pass-multiple-values'),
            pytest.param('to_int(scores)', {'scores': [9.9, -3.7, 5]}, [9, -3, 5], id='pass-array'),
        ],
    )
    def test_to_int(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

"""Tests for tcex.pleb.jmespath_functions_object_mixin (ObjectFunctionsMixin)."""

# standard library
import json
from typing import Any

# third-party
import jmespath
import pytest

# first-party
from tcex.pleb.jmespath_custom import jmespath_options


def _search(expr: str, data: Any) -> Any:
    """Evaluate a JMESPath expression with TcFunctions custom functions."""
    return jmespath.search(expr, data, options=jmespath_options())


class TestObjectFunctionsMixin:
    """Tests for object manipulation JMESPath functions."""

    # exclude_keys
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                "exclude_keys(obj, 'password')",
                {'obj': {'name': 'John', 'password': 'abc'}},
                {'name': 'John'},
                id='pass-removes-single-key',
            ),
            pytest.param(
                "exclude_keys(obj, 'password', 'secret')",
                {'obj': {'name': 'John', 'password': 'abc', 'secret': 'xyz'}},
                {'name': 'John'},
                id='pass-removes-multiple-keys',
            ),
            pytest.param(
                "exclude_keys(obj, 'missing')",
                {'obj': {'name': 'John'}},
                {'name': 'John'},
                id='pass-missing-key-no-error',
            ),
        ],
    )
    def test_exclude_keys(self, expr: str, data: dict, expected: dict) -> None:
        assert _search(expr, data) == expected

    # exclude_values
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'exclude_values(@, `null`)',
                {'name': 'John', 'age': None},
                {'name': 'John'},
                id='pass-removes-null',
            ),
            pytest.param(
                'exclude_values(@, `null`, ``)',
                {'name': 'John', 'age': None, 'city': ''},
                {'name': 'John'},
                id='pass-removes-null-and-empty-string',
            ),
            pytest.param(
                'exclude_values(@, `0`)',
                {'name': 'John', 'score': 0, 'level': 1},
                {'name': 'John', 'level': 1},
                id='pass-removes-zero',
            ),
            pytest.param(
                'exclude_values(@, `null`)',
                {'outer': {'inner': None, 'keep': 1}},
                {'outer': {'keep': 1}},
                id='pass-recursive-removal',
            ),
        ],
    )
    def test_exclude_values(self, expr: str, data: dict, expected: dict) -> None:
        assert _search(expr, data) == expected

    # include_keys
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                "include_keys(obj, 'name')",
                {'obj': {'name': 'John', 'age': 30, 'city': 'NY'}},
                {'name': 'John'},
                id='pass-keeps-single-key',
            ),
            pytest.param(
                "include_keys(obj, 'name', 'age')",
                {'obj': {'name': 'John', 'age': 30, 'city': 'NY'}},
                {'name': 'John', 'age': 30},
                id='pass-keeps-multiple-keys',
            ),
            pytest.param(
                "include_keys(obj, 'missing')",
                {'obj': {'name': 'John'}},
                {},
                id='pass-missing-key-returns-empty',
            ),
        ],
    )
    def test_include_keys(self, expr: str, data: dict, expected: dict) -> None:
        assert _search(expr, data) == expected

    # json_parse
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'json_parse(raw)',
                {'raw': '{"greeting": "hello"}'},
                {'greeting': 'hello'},
                id='pass-parses-object-string',
            ),
            pytest.param(
                'json_parse(raw)',
                {'raw': '[1,2,3]'},
                [1, 2, 3],
                id='pass-parses-array-string',
            ),
            pytest.param(
                'json_parse(a, b)',
                {'a': '{"x": 1}', 'b': '{"y": 2}'},
                [{'x': 1}, {'y': 2}],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'json_parse(raws)',
                {'raws': ['{"x": 1}', '{"y": 2}']},
                [{'x': 1}, {'y': 2}],
                id='pass-array',
            ),
        ],
    )
    def test_json_parse(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # json_stringify
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'json_stringify(payload)',
                {'payload': {'greeting': 'hello'}},
                {'greeting': 'hello'},
                id='pass-serializes-object',
            ),
            pytest.param(
                'json_stringify(payload)',
                {'payload': [1, 2, 3]},
                [1, 2, 3],
                id='pass-serializes-array',
            ),
        ],
    )
    def test_json_stringify(self, expr: str, data: dict, expected: Any) -> None:
        assert json.loads(_search(expr, data)) == expected

    # merge
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'merge(a, b)',
                {'a': {'roles': ['user']}, 'b': {'roles': ['admin']}},
                {'roles': ['user', 'admin']},
                id='pass-concatenates-arrays',
            ),
            pytest.param(
                'merge(a, b)',
                {'a': {'active': False}, 'b': {'active': True}},
                {'active': True},
                id='pass-replaces-scalar-values',
            ),
            pytest.param(
                'merge(a, b)',
                {'a': {'x': 1}, 'b': {'y': 2}},
                {'x': 1, 'y': 2},
                id='pass-adds-new-keys',
            ),
        ],
    )
    def test_merge(self, expr: str, data: dict, expected: dict) -> None:
        assert _search(expr, data) == expected

    # to_key_value_array
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'to_key_value_array(@)',
                {'name': 'John', 'age': 30},
                [{'key': 'name', 'value': 'John'}, {'key': 'age', 'value': 30}],
                id='pass-converts-object-to-key-value-pairs',
            ),
            pytest.param(
                'to_key_value_array(@)',
                {},
                [],
                id='pass-empty-object',
            ),
        ],
    )
    def test_to_key_value_array(self, expr: str, data: dict, expected: list) -> None:
        assert _search(expr, data) == expected

    # yaml_parse
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'yaml_parse(config)',
                {'config': 'key: value\nnum: 42'},
                {'key': 'value', 'num': 42},
                id='pass-parses-mapping',
            ),
            pytest.param(
                'yaml_parse(config)',
                {'config': '- a\n- b\n- c'},
                ['a', 'b', 'c'],
                id='pass-parses-list',
            ),
            pytest.param(
                'yaml_parse(a, b)',
                {'a': 'key: value', 'b': 'num: 42'},
                [{'key': 'value'}, {'num': 42}],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'yaml_parse(configs)',
                {'configs': ['key: value', 'num: 42']},
                [{'key': 'value'}, {'num': 42}],
                id='pass-array',
            ),
        ],
    )
    def test_yaml_parse(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

"""Tests for tcex.pleb.jmespath_functions_array_mixin (ArrayFunctionsMixin)."""

# standard library
from typing import Any

# third-party
import jmespath
import pytest

# first-party
from tcex.pleb.jmespath_custom import TcFunctions, jmespath_options


def _search(expr: str, data: Any) -> Any:
    """Evaluate a JMESPath expression with TcFunctions custom functions."""
    return jmespath.search(expr, data, options=jmespath_options())


class TestArrayFunctionsMixin:
    """Tests for array manipulation JMESPath functions."""

    # array_join
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                "array_join(items, 'new')",
                {'items': [1, 2]},
                [1, 2, 'new'],
                id='pass-array-input-scalar',
            ),
            pytest.param(
                'array_join(items, extra, `5`)',
                {'items': [1, 2], 'extra': [3, 4]},
                [1, 2, 3, 4, 5],
                id='pass-array-input-list-extended',
            ),
            pytest.param(
                "array_join(s, 'b')",
                {'s': 'a'},
                ['a', 'b'],
                id='pass-string-input-wrapped-and-appended',
            ),
            pytest.param(
                'array_join(s, extra)',
                {'s': 'a', 'extra': ['b', 'c']},
                ['a', 'b', 'c'],
                id='pass-string-input-list-extended',
            ),
            pytest.param(
                'array_join(items, `3`, `4`)',
                {'items': [1, 2]},
                [1, 2, 3, 4],
                id='pass-array-input-multiple-args',
            ),
            pytest.param(
                'array_join(items, blah)',
                {'items': [1, 2], 'extra': [3, 4], 'blah': None},
                [1, 2, None],
                id='pass-array-set-and-null',
            ),
            pytest.param(
                'array_join(items, blah)',
                {'items': [1, 2], 'extra': [3, 4]},
                [1, 2, None],
                id='pass-array-unset',
            ),
        ],
    )
    def test_array_join(self, expr: str, data: dict, expected: list) -> None:
        assert _search(expr, data) == expected

    # cartesian
    @pytest.mark.parametrize(
        'data,expected',
        [
            pytest.param(
                {'colors': ['red', 'blue'], 'sizes': ['S', 'M']},
                [['red', 'S'], ['red', 'M'], ['blue', 'S'], ['blue', 'M']],
                id='pass-two-by-two',
            ),
            pytest.param(
                {'colors': ['red', 'blue'], 'sizes': ['S', 'M', 'L']},
                [
                    ['red', 'S'],
                    ['red', 'M'],
                    ['red', 'L'],
                    ['blue', 'S'],
                    ['blue', 'M'],
                    ['blue', 'L'],
                ],
                id='pass-two-by-three',
            ),
            pytest.param(
                {'a': [], 'b': ['x']},
                [],
                id='pass-empty-produces-empty',
            ),
        ],
    )
    def test_cartesian(self, data: dict, expected: list) -> None:
        keys = list(data.keys())
        assert _search(f'cartesian([{keys[0]}, {keys[1]}])', data) == expected

    # chunk
    @pytest.mark.parametrize(
        'items,size,expected',
        [
            pytest.param([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]], id='pass-uneven-split'),
            pytest.param([1, 2, 3, 4], 2, [[1, 2], [3, 4]], id='pass-even-split'),
        ],
    )
    def test_chunk(self, items: list, size: int, expected: list) -> None:
        assert _search(f'chunk(items, `{size}`)', {'items': items}) == expected

    def test_chunk_size_zero_raises(self) -> None:
        tc = TcFunctions()
        with pytest.raises(ValueError, match='n must be at least one'):
            tc._func_chunk([1, 2, 3], 0)

    # compact
    @pytest.mark.parametrize(
        'items,expected',
        [
            pytest.param([1, None, 2, None, 3], [1, 2, 3], id='pass-removes-nulls'),
            pytest.param([None, None], [], id='pass-all-null-returns-empty'),
            pytest.param([1, 2, 3], [1, 2, 3], id='pass-no-nulls-unchanged'),
            pytest.param([], [], id='pass-empty-returns-empty'),
        ],
    )
    def test_compact(self, items: list, expected: list) -> None:
        assert _search('compact(items)', {'items': items}) == expected

    # dedup
    @pytest.mark.parametrize(
        'data,expected',
        [
            pytest.param(
                {'tags': ['a', 'b', 'a', 'c']},
                ['a', 'b', 'c'],
                id='pass-removes-duplicates',
            ),
            pytest.param(
                {'tags': [3, 1, 2, 1, 3]},
                [3, 1, 2],
                id='pass-preserves-first-occurrence-order',
            ),
            pytest.param(
                {'tags': [{'k': 1}, {'k': 2}, {'k': 1}]},
                [{'k': 1}, {'k': 2}],
                id='pass-dict-items-by-json-equality',
            ),
            pytest.param(
                {'tags': [{'k': 1, 'l': 1}, {'k': 2, 'l': 2}, {'l': 1, 'k': 1}]},
                [{'k': 1, 'l': 1}, {'k': 2, 'l': 2}],
                id='pass-dict-items-by-json-equality-unordered',
            ),
        ],
    )
    def test_dedup(self, data: dict, expected: list) -> None:
        assert _search('dedup(tags)', data) == expected

    # delete
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                "delete(locs, 'state')",
                {'locs': [{'city': 'Austin', 'state': 'TX'}, {'city': 'Denver', 'state': 'CO'}]},
                [{'city': 'Austin'}, {'city': 'Denver'}],
                id='pass-removes-key-from-objects',
            ),
            pytest.param(
                "delete(locs, 'state', 'city')",
                {'locs': [{'city': 'Austin', 'state': 'TX'}, {'city': 'Denver', 'state': 'CO'}]},
                [{}, {}],
                id='pass-removes-multiple-keys-from-objects',
            ),
            pytest.param(
                "delete(tags, 'TX')",
                {'tags': ['TX', 'CO', 'TX']},
                ['CO'],
                id='pass-removes-matching-string-value',
            ),
            pytest.param(
                "delete(tags, 'TX', 'CO')",
                {'tags': ['TX', 'CO', 'CA']},
                ['CA'],
                id='pass-removes-multiple-matching-string-values',
            ),
            pytest.param(
                "delete(items, 'missing')",
                {'items': [{'a': 1}, {'a': 2}]},
                [{'a': 1}, {'a': 2}],
                id='pass-missing-key-no-error',
            ),
        ],
    )
    def test_delete(self, expr: str, data: dict, expected: list) -> None:
        assert _search(expr, data) == expected

    # difference
    @pytest.mark.parametrize(
        'a,b,expected',
        [
            pytest.param([1, 2, 3, 4], [2, 4, 6], [1, 3], id='pass-left-only-elements'),
            pytest.param([1, 2], [1, 2], [], id='pass-identical-arrays-returns-empty'),
            pytest.param([1, 2, 3], [], [1, 2, 3], id='pass-empty-right-returns-left'),
            pytest.param([1, 1, 2], [3], [1, 2], id='pass-deduplicates-result'),
        ],
    )
    def test_difference(self, a: list, b: list, expected: list) -> None:
        assert _search('difference(a, b)', {'a': a, 'b': b}) == expected

    def test_difference_preserve_order_false_uses_set_difference(self) -> None:
        result = _search('difference(a, b, `false`)', {'a': [1, 2, 3, 4], 'b': [2, 4, 6]})
        assert set(result) == {1, 3}

    # expand
    def test_expand_duplicates_per_subvalue(self) -> None:
        data = [{'id': '1', 'urls': ['a.example.com', 'b.example.com'], 'cat': 'bad'}]
        result = _search('expand(@, &urls)', data)
        assert len(result) == 2
        assert result[0]['urls'] == 'a.example.com'
        assert result[1]['urls'] == 'b.example.com'
        assert result[0]['id'] == '1'

    def test_expand_empty_array_returns_empty(self) -> None:
        assert _search('expand(@, &urls)', []) == []

    # fill
    @pytest.mark.parametrize(
        'items,count,expected',
        [
            pytest.param(
                ['a', 'b'], 5, ['a', 'b', 'n/a', 'n/a', 'n/a'], id='pass-pads-short-array'
            ),
            pytest.param(['a', 'b', 'c'], 2, ['a', 'b'], id='pass-trims-long-array'),
        ],
    )
    def test_fill(self, items: list, count: int, expected: list) -> None:
        assert _search(f"fill(items, `{count}`, 'n/a')", {'items': items}) == expected

    # flatten_list
    @pytest.mark.parametrize(
        'data,expected',
        [
            pytest.param(
                {'nested': [1, [2, 3], [4, [5, 6]]]},
                [1, 2, 3, 4, 5, 6],
                id='pass-deeply-nested',
            ),
            pytest.param(
                {'nested': [1, 2, 3]},
                [1, 2, 3],
                id='pass-already-flat',
            ),
        ],
    )
    def test_flatten_list(self, data: dict, expected: list) -> None:
        assert _search('flatten_list(nested)', data) == expected

    # group_adjacent
    @pytest.mark.parametrize(
        'items,expected',
        [
            pytest.param(
                [{'cat': 'a', 'v': 1}, {'cat': 'a', 'v': 2}, {'cat': 'b', 'v': 3}],
                [[{'cat': 'a', 'v': 1}, {'cat': 'a', 'v': 2}], [{'cat': 'b', 'v': 3}]],
                id='pass-consecutive-groups',
            ),
            pytest.param(
                [{'cat': 'a'}, {'cat': 'b'}, {'cat': 'a'}],
                [[{'cat': 'a'}], [{'cat': 'b'}], [{'cat': 'a'}]],
                id='pass-non-adjacent-not-merged',
            ),
        ],
    )
    def test_group_adjacent(self, items: list, expected: list) -> None:
        assert _search('group_adjacent(items, &cat)', {'items': items}) == expected

    # group_by
    @pytest.mark.parametrize(
        'items,expected',
        [
            pytest.param(
                [{'type': 'x', 'val': 1}, {'type': 'y', 'val': 2}, {'type': 'x', 'val': 3}],
                {
                    'x': [{'type': 'x', 'val': 1}, {'type': 'x', 'val': 3}],
                    'y': [{'type': 'y', 'val': 2}],
                },
                id='pass-groups-by-key',
            ),
            pytest.param([], [], id='pass-empty-returns-empty'),
        ],
    )
    def test_group_by(self, items: list, expected: Any) -> None:
        assert _search('group_by(items, &type)', {'items': items}) == expected

    # index_array
    @pytest.mark.parametrize(
        'expr,expected_first,expected_second',
        [
            pytest.param(
                "index_array(items, 'idx')",
                0,
                1,
                id='pass-default-start-at-zero',
            ),
            pytest.param(
                "index_array(items, 'idx', `1`)",
                1,
                2,
                id='pass-custom-start-at-one',
            ),
            pytest.param(
                "index_array(items, 'idx', `a`)",
                1,
                2,
                id='fail-non-numeric-start',
                marks=pytest.mark.xfail,
            ),
        ],
    )
    def test_index_array(self, expr: str, expected_first: int, expected_second: int) -> None:
        result = _search(expr, {'items': [{'name': 'a'}, {'name': 'b'}]})
        assert result[0]['idx'] == expected_first
        assert result[1]['idx'] == expected_second

    # intersect
    @pytest.mark.parametrize(
        'a,b,expected',
        [
            pytest.param([1, 2, 3, 4], [2, 4, 6], [2, 4], id='pass-common-elements'),
            pytest.param([1, 2], [3, 4], [], id='pass-no-common-elements'),
            pytest.param([1, 1, 2], [1], [1], id='pass-preserves-uniqueness'),
            pytest.param([4, 3, 2, 1], [1, 2, 3, 4], [1, 2, 3, 4], id='pass-preserves-left-order'),
        ],
    )
    def test_intersect(self, a: list, b: list, expected: list) -> None:
        assert _search('intersect(a, b)', {'a': a, 'b': b}) == expected

    def test_intersect_preserve_order_true_preserves_left_order(self) -> None:
        data = {'a': [4, 3, 2, 1], 'b': [1, 2, 3, 4]}
        assert _search('intersect(a, b, `true`)', data) == [4, 3, 2, 1]

    def test_intersect_preserve_order_false_uses_set_intersection(self) -> None:
        data = {'a': [1, 2, 3, 4], 'b': [2, 4, 6]}
        result = _search('intersect(a, b, `false`)', data)
        assert set(result) == {2, 4}

    # list_join — commented out for further review before next release
    #
    # TODO: test multiple people with the same teamId and team with no people
    # def test_list_join_produces_outer_join(self) -> None:
    #     data = {
    #         'people': [{'teamId': 1, 'name': 'Alice'}, {'teamId': 2, 'name': 'Bob'}],
    #         'teams': [{'id': 1, 'team': 'Red'}, {'id': 3, 'team': 'Blue'}],
    #     }
    #     result = _search('list_join(people, teams, &teamId, &id)', data)
    #     assert len(result) == 3
    #     assert all('__index' in entry for entry in result)
    #     assert all('left' in entry for entry in result)
    #     assert all('right' in entry for entry in result)
    #
    # def test_list_join_matching_entries_grouped(self) -> None:
    #     data = {'left': [{'k': 1, 'v': 'a'}], 'right': [{'k': 1, 'v': 'b'}]}
    #     result = _search('list_join(left, right, &k, &k)', data)
    #     assert len(result) == 1
    #     assert result[0]['left'] == [{'k': 1, 'v': 'a'}]
    #     assert result[0]['right'] == [{'k': 1, 'v': 'b'}]
    #
    # def test_list_join_skips_none_items_but_includes_null_valued(self) -> None:
    #     # None elements (unset) are skipped; objects with a null key value are included.
    #     data = {
    #         'left': [None, {'k': 1, 'v': 'a'}, {'k': None, 'v': 'null-key'}],
    #         'right': [{'k': 1, 'v': 'b'}, None],
    #     }
    #     result = _search('list_join(left, right, &k, &k)', data)
    #     keys = [entry['__index'] for entry in result]
    #     # None items are dropped, so only key=1 and key=None(explicit) groups remain
    #     left_items = [item for entry in result for item in entry['left']]
    #     right_items = [item for entry in result for item in entry['right']]
    #     assert {'k': 1, 'v': 'a'} in left_items
    #     assert {'k': None, 'v': 'null-key'} in left_items
    #     assert {'k': 1, 'v': 'b'} in right_items
    #     assert len(keys) == 2  # key=1 group and key=None group; no extra entry from None items

    # null_leaf
    def test_null_leaf_returns_null_for_missing_key(self) -> None:
        data = {'locs': [{'city': 'Austin', 'state': 'TX'}, {'city': 'Denver'}]}
        assert _search("null_leaf(locs, 'state')", data) == ['TX', None]

    # symmetric_difference
    @pytest.mark.parametrize(
        'a,b,expected',
        [
            pytest.param([1, 2, 3, 4], [2, 4, 6], [1, 3, 6], id='pass-left-then-right-only'),
            pytest.param([1, 2], [1, 2], [], id='pass-identical-arrays-returns-empty'),
            pytest.param([1, 2, 3], [], [1, 2, 3], id='pass-empty-right-returns-left'),
            pytest.param([], [1, 2, 3], [1, 2, 3], id='pass-empty-left-returns-right'),
        ],
    )
    def test_symmetric_difference(self, a: list, b: list, expected: list) -> None:
        assert _search('symmetric_difference(a, b)', {'a': a, 'b': b}) == expected

    def test_symmetric_difference_preserve_order_false_uses_set(self) -> None:
        result = _search('symmetric_difference(a, b, `false`)', {'a': [1, 2, 3, 4], 'b': [2, 4, 6]})
        assert set(result) == {1, 3, 6}

    # union
    @pytest.mark.parametrize(
        'a,b,expected',
        [
            pytest.param([1, 2, 3], [2, 3, 4], [1, 2, 3, 4], id='pass-unique-elements-from-both'),
            pytest.param([1, 2], [1, 2], [1, 2], id='pass-identical-arrays-deduplicates'),
            pytest.param([1, 2], [], [1, 2], id='pass-empty-right-returns-left'),
            pytest.param([], [1, 2], [1, 2], id='pass-empty-left-returns-right'),
        ],
    )
    def test_union(self, a: list, b: list, expected: list) -> None:
        assert _search('union(a, b)', {'a': a, 'b': b}) == expected

    def test_union_preserve_order_false_uses_set_union(self) -> None:
        result = _search('union(a, b, `false`)', {'a': [1, 2, 3], 'b': [2, 3, 4]})
        assert set(result) == {1, 2, 3, 4}

    # zip
    def test_zip_transposes_arrays(self) -> None:
        result = _search('zip([first, last])', {'first': ['a', 'b'], 'last': ['x', 'y']})
        assert list(result[0]) == ['a', 'x']
        assert list(result[1]) == ['b', 'y']

    def test_zip_pads_short_array_with_null(self) -> None:
        result = _search('zip([a, b])', {'a': [1, 2, 3], 'b': [4, 5]})
        assert result[2][1] is None

    def test_zip_with_fill_value(self) -> None:
        tc = TcFunctions()
        assert list(tc._func_zip([[1, 2, 3], [4, 5]], 'x')[2]) == [3, 'x']

    # zip_merge
    def test_zip_merge_combines_by_position(self) -> None:
        data = {'names': [{'name': 'Alice'}, {'name': 'Bob'}], 'ages': [{'age': 30}, {'age': 25}]}
        result = _search('zip_merge(names, ages)', data)
        assert result == [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]

    # zip_to_objects
    @pytest.mark.parametrize(
        'keys,values,fill_value,expected',
        [
            pytest.param(
                ['first', 'last'],
                [['bob', 'joe'], ['smith', 'jones']],
                None,
                [{'first': 'bob', 'last': 'smith'}, {'first': 'joe', 'last': 'jones'}],
                id='pass-creates-objects',
            ),
            pytest.param(
                ['k'],
                [['a', 'b', 'c']],
                'n/a',
                [{'k': 'a'}, {'k': 'b'}, {'k': 'c'}],
                id='pass-pads-with-fill-value',
            ),
        ],
    )
    def test_zip_to_objects(
        self, keys: list, values: list, fill_value: Any, expected: list
    ) -> None:
        tc = TcFunctions()
        assert tc._func_zip_to_objects(keys, values, fill_value=fill_value) == expected

    def test_zip_to_objects_mismatched_lengths_raises(self) -> None:
        tc = TcFunctions()
        with pytest.raises(RuntimeError):
            tc._func_zip_to_objects(['a'], [['x'], ['y']])

"""Tests for tcex.pleb.jmespath_functions_string_mixin (StringFunctionsMixin)."""

import base64
import json
from typing import Any

import jmespath
import pytest

from tcex.pleb.jmespath_custom import TcFunctions, jmespath_options


def _search(expr: str, data: Any) -> Any:
    """Evaluate a JMESPath expression with TcFunctions custom functions."""
    return jmespath.search(expr, data, options=jmespath_options())


class TestStringFunctionsMixin:
    """Tests for string manipulation JMESPath functions."""

    # base64_decode
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'base64_decode(encoded)',
                {'encoded': 'SGVsbG8gV29ybGQh'},
                'Hello World!',
                id='pass-string',
            ),
            pytest.param(
                'base64_decode(a, b)',
                {'a': 'SGVsbG8gV29ybGQh', 'b': 'Zm9v'},
                ['Hello World!', 'foo'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'base64_decode(encoded)',
                {'encoded': ['SGVsbG8gV29ybGQh', 'Zm9v']},
                ['Hello World!', 'foo'],
                id='pass-array',
            ),
        ],
    )
    def test_base64_decode(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # base64_encode
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'base64_encode(message)',
                {'message': 'Hello World!'},
                'SGVsbG8gV29ybGQh',
                id='pass-string',
            ),
        ],
    )
    def test_base64_encode(self, expr: str, data: dict, expected: str) -> None:
        assert _search(expr, data) == expected

    def test_base64_encode_encodes_object_as_json(self) -> None:
        tc = TcFunctions()
        result = tc._func_base64_encode({'k': 'v'})
        assert json.loads(base64.b64decode(result).decode('utf-8')) == {'k': 'v'}

    def test_base64_encode_roundtrip_with_base64_decode(self) -> None:
        tc = TcFunctions()
        original = 'Hello World!'
        assert tc._func_base64_decode(tc._func_base64_encode(original)) == original

    # capitalize
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'capitalize(name)',
                {'name': 'john doe'},
                'John Doe',
                id='pass-single-string',
            ),
            pytest.param(
                'capitalize(first, last)',
                {'first': 'john', 'last': 'doe'},
                ['John', 'Doe'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'capitalize(names)',
                {'names': ['john doe', 'jane smith']},
                ['John Doe', 'Jane Smith'],
                id='pass-array',
            ),
        ],
    )
    def test_capitalize(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # decode_url
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'decode_url(encoded)',
                {'encoded': 'hello%20world%21'},
                'hello world!',
                id='pass-percent-encoded',
            ),
            pytest.param(
                'decode_url(encoded)',
                {'encoded': 'https://www.example.com/hello%20world%21?foo=bar%20baz&x=1%2B2'},
                'https://www.example.com/hello world!?foo=bar baz&x=1+2',
                id='pass-percent-encoded-url-with-query-params',
            ),
            pytest.param(
                'decode_url(a, b)',
                {'a': 'hello%20world', 'b': 'foo%21bar'},
                ['hello world', 'foo!bar'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'decode_url(encoded_urls)',
                {'encoded_urls': ['hello%20world', 'foo%21bar']},
                ['hello world', 'foo!bar'],
                id='pass-array',
            ),
        ],
    )
    def test_decode_url(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # defang
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'defang(indicator)',
                {'indicator': 'https://malicious.example.com'},
                'hxxps[:]//malicious[.]example[.]com',
                id='pass-url-string',
            ),
            pytest.param(
                'defang(indicator)',
                {'indicator': '192.168.1.1'},
                '192[.]168[.]1[.]1',
                id='pass-ip-address-string',
            ),
            pytest.param(
                'defang(url, ip)',
                {'url': 'https://evil.com', 'ip': '192.168.1.1'},
                ['hxxps[:]//evil[.]com', '192[.]168[.]1[.]1'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'defang(indicators)',
                {'indicators': ['https://evil.com', '192.168.1.1']},
                ['hxxps[:]//evil[.]com', '192[.]168[.]1[.]1'],
                id='pass-array',
            ),
        ],
    )
    def test_defang(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # encode_url
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'encode_url(path)',
                {'path': 'hello world!'},
                'hello%20world%21',
                id='pass-encodes-spaces-and-special-chars',
            ),
            pytest.param(
                'encode_url(url)',
                {'url': 'https://www.example.com/search?q=hello world&page=1'},
                'https%3A//www.example.com/search%3Fq%3Dhello%20world%26page%3D1',
                id='pass-full-url-with-query-params',
            ),
            pytest.param(
                'encode_url(a, b)',
                {'a': 'hello world', 'b': 'foo!bar'},
                ['hello%20world', 'foo%21bar'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'encode_url(paths)',
                {'paths': ['hello world', 'foo!bar']},
                ['hello%20world', 'foo%21bar'],
                id='pass-array',
            ),
        ],
    )
    def test_encode_url(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # equal_fold
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'equal_fold(a, b)',
                {'a': 'Engineering', 'b': 'engineering'},
                True,
                id='pass-case-insensitive-match',
            ),
            pytest.param(
                'equal_fold(a, b)',
                {'a': 'foo', 'b': 'bar'},
                False,
                id='pass-different-strings',
            ),
        ],
    )
    def test_equal_fold(self, expr: str, data: dict, expected: bool) -> None:
        assert _search(expr, data) is expected

    # lower
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'lower(text)',
                {'text': 'HELLO'},
                'hello',
                id='pass-string',
            ),
            pytest.param(
                'lower(first, last)',
                {'first': 'JOHN', 'last': 'DOE'},
                ['john', 'doe'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'lower(texts)',
                {'texts': ['FOO', 'BAR']},
                ['foo', 'bar'],
                id='pass-array',
            ),
        ],
    )
    def test_lower(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # pattern_match
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'pattern_match(pattern, ip)',
                {'pattern': '192.168.*', 'ip': '192.168.1.100'},
                True,
                id='pass-wildcard-match',
            ),
            pytest.param(
                'pattern_match(pattern, ip)',
                {'pattern': '192.168.*', 'ip': '10.0.0.1'},
                False,
                id='pass-no-match',
            ),
            pytest.param(
                'pattern_match(pattern, ip)',
                {'pattern': 'hel?o', 'ip': 'hello'},
                True,
                id='pass-question-mark-wildcard',
            ),
        ],
    )
    def test_pattern_match(self, expr: str, data: dict, expected: bool) -> None:
        assert _search(expr, data) is expected

    # refang
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'refang(indicator)',
                {'indicator': 'hxxps://malicious[.]example[.]com'},
                'https://malicious.example.com',
                id='pass-url-string',
            ),
            pytest.param(
                'refang(indicator)',
                {'indicator': '192[.]168[.]1[.]1'},
                '192.168.1.1',
                id='pass-ip-address',
            ),
            pytest.param(
                'refang(url, ip)',
                {'url': 'hxxps[:]//evil[.]com', 'ip': '192[.]168[.]1[.]1'},
                ['https://evil.com', '192.168.1.1'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'refang(indicators)',
                {'indicators': ['hxxps://evil[.]com', '192[.]168[.]1[.]1']},
                ['https://evil.com', '192.168.1.1'],
                id='pass-array',
            ),
        ],
    )
    def test_refang(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # regex
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'regex(pattern, text)',
                {'pattern': 'hello', 'text': 'say hello world'},
                'hello',
                id='pass-no-groups-returns-full-match',
            ),
            pytest.param(
                'regex(pattern, text)',
                {'pattern': 'xyz', 'text': 'no match here'},
                None,
                id='pass-no-match-returns-null',
            ),
            pytest.param(
                'regex(pattern, text)',
                {'pattern': r'IP:(\d+\.\d+\.\d+\.\d+)', 'text': 'Connection from IP:192.168.1.1'},
                ['192.168.1.1'],
                id='pass-capture-group-returns-list',
            ),
        ],
    )
    def test_regex(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # regex_match
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'regex_match(pattern, port)',
                {'pattern': '[0-9]+', 'port': '8080'},
                True,
                id='pass-digits-match',
            ),
            pytest.param(
                'regex_match(pattern, port)',
                {'pattern': '[0-9]+', 'port': 'abc'},
                False,
                id='pass-no-match',
            ),
            pytest.param(
                'regex_match(pattern, port)',
                {'pattern': r'\d+', 'port': 8080},
                True,
                id='pass-number-input',
            ),
        ],
    )
    def test_regex_match(self, expr: str, data: dict, expected: bool) -> None:
        assert _search(expr, data) is expected

    # regex_replace
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'regex_replace(pattern, text, replacement)',
                {'pattern': 'Banana', 'text': 'Banana Banana', 'replacement': 'Apple'},
                'Apple Apple',
                id='pass-replaces-all-in-string',
            ),
            pytest.param(
                'regex_replace(pattern, texts, replacement)',
                {'pattern': 'bad', 'texts': ['bad news', 'bad luck'], 'replacement': 'good'},
                ['good news', 'good luck'],
                id='pass-replaces-in-array',
            ),
            pytest.param(
                "regex_replace('Ban\\w+', text, 'Apple')",
                {'text': 'Banana Banana'},
                'Apple Apple',
                id='pass-literal-pattern-and-replacement-string',
            ),
            pytest.param(
                "regex_replace('bad', texts, 'good')",
                {'texts': ['bad news', 'bad luck']},
                ['good news', 'good luck'],
                id='pass-literal-pattern-and-replacement-array',
            ),
        ],
    )
    def test_regex_replace(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # replace
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'replace(message, search, replacement)',
                {'message': 'hello world world', 'search': 'world', 'replacement': 'there'},
                'hello there there',
                id='pass-replaces-all-occurrences',
            ),
            pytest.param(
                'replace(message, search, replacement)',
                {'message': 'hello', 'search': 'xyz', 'replacement': 'abc'},
                'hello',
                id='pass-no-match-unchanged',
            ),
            pytest.param(
                "replace(message, 'world', 'there')",
                {'message': 'hello world world'},
                'hello there there',
                id='pass-literal-search-and-replacement',
            ),
        ],
    )
    def test_replace(self, expr: str, data: dict, expected: str) -> None:
        assert _search(expr, data) == expected

    # split
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'split(text)', {'text': 'a,b,c'}, ['a', 'b', 'c'], id='pass-default-comma-delimiter'
            ),
            pytest.param(
                'split(text, delimiter)',
                {'text': 'a|b|c', 'delimiter': '|'},
                ['a', 'b', 'c'],
                id='pass-custom-delimiter',
            ),
            pytest.param(
                'split(texts)',
                {'texts': ['a,b', 'c,d']},
                [['a', 'b'], ['c', 'd']],
                id='pass-array-of-strings',
            ),
        ],
    )
    def test_split(self, expr: str, data: dict, expected: list) -> None:
        assert _search(expr, data) == expected

    # string_interpolate
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'string_interpolate(template, params)',
                {'template': 'Hello, {name}!', 'params': {'name': 'World'}},
                'Hello, World!',
                id='pass-named-params',
            ),
            pytest.param(
                'string_interpolate(template, params)',
                {'template': '{0} {1}', 'params': ['foo', 'bar']},
                'foo bar',
                id='pass-positional-params',
            ),
            pytest.param(
                'string_interpolate(template, params)',
                {'template': '{a}', 'params': {'a': None}},
                '',
                id='pass-null-value-becomes-empty',
            ),
        ],
    )
    def test_string_interpolate(self, expr: str, data: dict, expected: str) -> None:
        assert _search(expr, data) == expected

    # trim
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'trim(text)',
                {'text': '  hello  '},
                'hello',
                id='pass-removes-leading-trailing-whitespace',
            ),
            pytest.param(
                'trim(text)', {'text': 'hello'}, 'hello', id='pass-no-whitespace-unchanged'
            ),
            pytest.param(
                'trim(first, last)',
                {'first': '  hello  ', 'last': '  world  '},
                ['hello', 'world'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'trim(texts)',
                {'texts': ['  hello  ', '  world  ']},
                ['hello', 'world'],
                id='pass-array',
            ),
        ],
    )
    def test_trim(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

    # upper
    @pytest.mark.parametrize(
        'expr,data,expected',
        [
            pytest.param(
                'upper(text)',
                {'text': 'hello'},
                'HELLO',
                id='pass-string',
            ),
            pytest.param(
                'upper(first, last)',
                {'first': 'john', 'last': 'doe'},
                ['JOHN', 'DOE'],
                id='pass-multiple-strings',
            ),
            pytest.param(
                'upper(texts)',
                {'texts': ['hello', 'world']},
                ['HELLO', 'WORLD'],
                id='pass-array',
            ),
        ],
    )
    def test_upper(self, expr: str, data: dict, expected: Any) -> None:
        assert _search(expr, data) == expected

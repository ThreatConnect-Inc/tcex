"""Tests for tcex.pleb.jmespath_functions_crypto_mixin (CryptoFunctionsMixin)."""

# standard library
import re

# third-party
import jmespath
import pytest

# first-party
from tcex.pleb.jmespath_custom import jmespath_options


def _search(expr: str, data) -> any:
    """Evaluate a JMESPath expression with TcFunctions custom functions."""
    return jmespath.search(expr, data, options=jmespath_options())


class TestCryptoFunctionsMixin:
    """Tests for cryptographic and identity JMESPath functions."""

    # semver_compare
    @pytest.mark.parametrize(
        'version,constraint,expected',
        [
            pytest.param('1.5.3', '>=1.0.0,<2.0.0', True, id='pass-in-range'),
            pytest.param('1.5.3', '>=2.0.0', False, id='pass-out-of-range'),
            pytest.param('1.0.0', '==1.0.0', True, id='pass-exact-version'),
            pytest.param('1.0.0', '!=1.0.0', False, id='pass-not-equal'),
        ],
    )
    def test_semver_compare(self, version: str, constraint: str, expected: bool) -> None:
        assert _search(f"semver_compare(v, '{constraint}')", {'v': version}) is expected

    # uuid
    def test_uuid_returns_valid_uuid4(self) -> None:
        result = _search('uuid()', {})
        assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', result)

    def test_uuid_generates_unique_values(self) -> None:
        assert _search('uuid()', {}) != _search('uuid()', {})

    # uuid5
    def test_uuid5_is_deterministic(self) -> None:
        assert _search('uuid5(v)', {'v': 'my-article'}) == _search('uuid5(v)', {'v': 'my-article'})

    def test_uuid5_different_inputs_produce_different_uuids(self) -> None:
        assert _search('uuid5(v)', {'v': 'aaa'}) != _search('uuid5(v)', {'v': 'bbb'})

    def test_uuid5_returns_valid_uuid_format(self) -> None:
        assert re.match(r'^[0-9a-f-]{36}$', _search('uuid5(v)', {'v': 'my-article'}))

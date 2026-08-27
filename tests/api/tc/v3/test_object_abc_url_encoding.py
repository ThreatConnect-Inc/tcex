"""TcEx Framework Module.

Regression tests for percent-encoding of a V3 object's fallback unique-id when it is spliced into a
request URL path (ESUP-4662 / upstream tcex 4.0 PR #412).

Encoding is centralized in ``ObjectABC._calculate_unique_id(encode_value=True)``: only the
summary-fallback branch is percent-encoded, and only when the caller opts in. Callers that build a
URL path segment (``url()``, ``get()``, ``delete()``, ``update()``, and the parent unique-id
captured in ``_iterate_over_sublist()`` for the generated ``remove()`` methods) pass
``encode_value=True``; callers that build a TQL search clause or a JSON removal-match filter use the
raw (default) call.

These are credential-free unit tests: they construct V3 objects with ``session=None`` and never hit
the network. ``ObjectABC.__init__`` only stores the session reference and never touches it during
construction, ``_calculate_unique_id()``, or ``url()``.
"""

# standard library
from unittest.mock import MagicMock

# third-party
import pytest

# first-party
from tcex.api.tc.v3.groups.group import Group
from tcex.api.tc.v3.indicators.indicator import Indicator
from tcex.api.tc.v3.security_labels.security_label import SecurityLabel
from tcex.api.tc.v3.tags.tag import Tag


class TestObjectAbcUrlEncoding:
    """Test URL percent-encoding of unique-id path segments in the V3 client."""

    @staticmethod
    @pytest.mark.parametrize(
        argnames='method',
        argvalues=[
            pytest.param('GET', id='get'),
            pytest.param('PUT', id='put'),
            pytest.param('DELETE', id='delete'),
        ],
    )
    @pytest.mark.parametrize(
        argnames='summary,expected_segment',
        argvalues=[
            pytest.param(
                # full URL-type indicator summary - the ESUP-4662 repro value
                'https://test.local',
                'https%3A%2F%2Ftest.local',
                id='full-url',
            ),
            pytest.param(
                # forward slash must not create extra path segments
                'a/b',
                'a%2Fb',
                id='forward-slash',
            ),
            pytest.param(
                # hash must not be treated as a URL fragment
                'a#b',
                'a%23b',
                id='hash',
            ),
        ],
    )
    def test_url_encodes_summary_fallback(method, summary, expected_segment):
        """url() percent-encodes an Indicator summary used as the fallback unique-id."""
        indicator = Indicator(session=None, summary=summary)

        result = indicator.url(method)

        expected = f'/v3/indicators/{expected_segment}'
        assert result == expected, f'{method} url of {result} != {expected}'

    @staticmethod
    def test_url_post_returns_endpoint_without_id():
        """url() for POST returns the bare endpoint, unaffected by the encoding guard."""
        indicator = Indicator(session=None, summary='https://test.local')

        result = indicator.url('POST')

        assert result == '/v3/indicators', f'POST url of {result} != /v3/indicators'

    @staticmethod
    def test_url_none_unique_id_no_typeerror():
        """url() with no resolvable unique-id builds the legacy .../None path, no TypeError."""
        indicator = Indicator(session=None)

        result = indicator.url('GET')

        assert result == '/v3/indicators/None', f'url of {result} != /v3/indicators/None'

    @staticmethod
    @pytest.mark.parametrize(
        argnames='object_class',
        argvalues=[
            pytest.param(Indicator, id='indicator'),
            pytest.param(Group, id='group'),
            pytest.param(Tag, id='tag'),
            pytest.param(SecurityLabel, id='security-label'),
        ],
    )
    @pytest.mark.parametrize(
        argnames='parent_unique_id',
        argvalues=[
            pytest.param(
                # an already-encoded parent Indicator summary (full URL)
                'https%3A%2F%2Fparent.local',
                id='full-url',
            ),
            pytest.param(
                # already-encoded reserved slash + hash in the parent unique-id
                'a%2Fb%23c',
                id='slash-and-hash',
            ),
        ],
    )
    def test_remove_passes_through_encoded_parent_unique_id(object_class, parent_unique_id):
        """remove() splices _parent_data['unique_id'] into its URL verbatim, without re-encoding.

        Under the centralized design, encoding happens once in _iterate_over_sublist() (via
        _calculate_unique_id(encode_value=True)) when _parent_data is populated. remove() trusts the
        value is already correct and must not double-encode it.
        """
        obj = object_class(session=None, id=99)
        obj._parent_data = {'api_endpoint': '/v3/groups', 'unique_id': parent_unique_id}  # noqa: SLF001

        # mock the instance _request so no network occurs; pre-set request for the return value.
        obj._request = MagicMock()  # noqa: SLF001
        obj.request = MagicMock()

        obj.remove()

        url = obj._request.call_args.kwargs['url']  # noqa: SLF001
        expected = f'/v3/groups/{parent_unique_id}'
        assert url == expected, (
            f'remove url of {url} != {expected} (must pass encoded value through)'
        )


class TestCalculateUniqueId:
    """Test ObjectABC._calculate_unique_id - the single place encoding logic now lives."""

    @staticmethod
    @pytest.mark.parametrize(
        argnames='summary,expected_value',
        argvalues=[
            pytest.param(
                # full URL-type indicator summary - the ESUP-4662 repro value
                'https://test.local',
                'https%3A%2F%2Ftest.local',
                id='full-url',
            ),
            pytest.param(
                # forward slash must be percent-encoded so it stays one path segment
                'a/b',
                'a%2Fb',
                id='forward-slash',
            ),
            pytest.param(
                # hash must be percent-encoded so it is not read as a URL fragment
                'a#b',
                'a%23b',
                id='hash',
            ),
        ],
    )
    def test_encode_value_true_encodes_summary(summary, expected_value):
        """encode_value=True percent-encodes the summary while keeping filter='summary'."""
        indicator = Indicator(session=None, summary=summary)

        result = indicator._calculate_unique_id(encode_value=True)  # noqa: SLF001

        assert result == {'filter': 'summary', 'value': expected_value}, (
            f'encoded unique_id of {result} != summary/{expected_value}'
        )

    @staticmethod
    @pytest.mark.parametrize(
        argnames='summary',
        argvalues=[
            pytest.param('https://test.local', id='full-url'),
            pytest.param('a/b', id='forward-slash'),
            pytest.param('a#b', id='hash'),
        ],
    )
    def test_encode_value_false_returns_raw_summary(summary):
        """encode_value=False (default) returns the RAW summary - required for correctness.

        The raw call feeds TQL search-clause construction in _iterate_over_sublist() and the JSON
        removal-match filter in the generated remove() methods. Percent-encoding here would corrupt
        a TQL search or the removal-match filter sent to the real API (the API expects the literal
        value, not a URL-encoded one), so the default must stay unencoded.
        """
        indicator = Indicator(session=None, summary=summary)

        result = indicator._calculate_unique_id()  # noqa: SLF001

        assert result == {'filter': 'summary', 'value': summary}, (
            f'raw unique_id of {result} != summary/{summary}'
        )

    @staticmethod
    @pytest.mark.parametrize(
        argnames='encode_value',
        argvalues=[
            pytest.param(True, id='encode-true'),
            pytest.param(False, id='encode-false'),
        ],
    )
    def test_encode_value_no_effect_on_id_branch(encode_value):
        """The id branch (int) is unaffected by encode_value - only summary is encoded."""
        indicator = Indicator(session=None, id=123, summary='a/b')

        result = indicator._calculate_unique_id(encode_value=encode_value)  # noqa: SLF001

        assert result == {'filter': 'id', 'value': 123}, (
            f'id-branch unique_id of {result} != id/123'
        )

    @staticmethod
    @pytest.mark.parametrize(
        argnames='encode_value',
        argvalues=[
            pytest.param(True, id='encode-true'),
            pytest.param(False, id='encode-false'),
        ],
    )
    def test_encode_value_no_effect_on_xid_branch(encode_value):
        """The xid branch (string) is unaffected by encode_value - reserved chars stay literal."""
        group = Group(session=None, xid='a/b#c')

        result = group._calculate_unique_id(encode_value=encode_value)  # noqa: SLF001

        assert result == {'filter': 'xid', 'value': 'a/b#c'}, (
            f'xid-branch unique_id of {result} != xid/a/b#c'
        )

    @staticmethod
    def test_encode_value_true_summary_none_no_typeerror():
        """encode_value=True with a None summary returns value=None without calling quote(None)."""
        indicator = Indicator(session=None)

        result = indicator._calculate_unique_id(encode_value=True)  # noqa: SLF001

        assert result == {'filter': 'summary', 'value': None}, (
            f'none-summary unique_id of {result} != summary/None'
        )

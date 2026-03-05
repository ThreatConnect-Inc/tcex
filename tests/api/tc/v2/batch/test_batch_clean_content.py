"""Tests for BatchCleaner."""

import json
import logging
import re
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from deepdiff.diff import DeepDiff

from tcex import TcEx
from tcex.api.tc.v2.batch.batch_cleaner import BatchCleaner

# ---------------------------------------------------------------------------
# Test hashes (valid lengths: md5=32, sha1=40, sha256=64)
# ---------------------------------------------------------------------------
MD5: str = 'a' * 32
MD5_ALT: str = 'f' * 32
SHA1: str = 'b' * 40
SHA256: str = 'c' * 64

ATTRIBUTE_CONFIG: dict[str, dict[str, int]] = {
    'Description': {'maxSize': 500},
    'Source': {'maxSize': 20},
    'Events': {'maxSize': 100},
}


# ---------------------------------------------------------------------------
# Mock helpers for BatchCleaner construction
# ---------------------------------------------------------------------------
def _noop_mitre_tags() -> Mock:
    """Return a mock MitreTags whose lookups always return None.

    Returns:
        A Mock standing in for a MitreTags instance.
    """
    mock = Mock()
    mock.get_by_id_regex = Mock(return_value=None)
    return mock


def _mock_mitre_tags(data: dict[str, str]) -> Mock:
    """Return a mock MitreTags that resolves technique ids from *data*.

    Args:
        data: A dict mapping technique ids to names (e.g. ``{"T1059": "..."}``).

    Returns:
        A Mock whose ``get_by_id_regex`` formats matching tags.
    """
    mock = Mock()

    def get_by_id_regex(value: str, default: str | None = None) -> str | None:
        matches = re.findall(r'([Tt]\d+(?:\.\d+)?)', value)
        if len(matches) != 1:
            return default
        id_ = matches[0].upper()
        name = data.get(id_)
        return f'{id_} - {name}' if name else default

    mock.get_by_id_regex = get_by_id_regex
    return mock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_indicator(
    summary: str | None, *, indicator_type: str = 'Address', **fields: Any
) -> dict[str, Any]:
    """Build an indicator dictionary.

    Args:
        summary: The indicator summary value.
        indicator_type: ThreatConnect indicator type name.
        **fields: Additional indicator fields to include.

    Returns:
        A dict representing a batch indicator.
    """
    return {'summary': summary, 'type': indicator_type, **fields}


def make_file_indicator(
    summary: str, *, filename: str | None = None, **fields: Any
) -> dict[str, Any]:
    """Build a File indicator, optionally with a fileOccurrence.

    Args:
        summary: The file hash summary string (e.g. ``md5 : sha1 : sha256``).
        filename: If provided, a fileOccurrence entry is added with this name.
        **fields: Additional indicator fields to include.

    Returns:
        A dict representing a batch File indicator.
    """
    indicator = make_indicator(summary, indicator_type='File', **fields)
    if filename is not None:
        indicator['fileOccurrence'] = [{'fileName': filename}]
    return indicator


def make_group(name: str, *, group_type: str = 'Adversary', **fields: Any) -> dict[str, Any]:
    """Build a group dictionary.

    Args:
        name: The group name.
        group_type: ThreatConnect group type name.
        **fields: Additional group fields to include.

    Returns:
        A dict representing a batch group.
    """
    return {'name': name, 'type': group_type, **fields}


def make_content(
    indicators: list[dict[str, Any]] | None = None,
    groups: list[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Build a batch content dictionary.

    Args:
        indicators: List of indicator dicts.
        groups: List of group dicts.

    Returns:
        A dict with ``indicator`` and ``group`` keys.
    """
    return {'indicator': indicators or [], 'group': groups or []}


def make_attributes(*type_value_pairs: tuple[str, str]) -> list[dict[str, str]]:
    """Build an attribute list from (type, value) pairs.

    Args:
        *type_value_pairs: Tuples of ``(attribute_type, value)``.

    Returns:
        A list of attribute dicts.

    Example::

        make_attributes(('Description', 'hello'), ('Source', 'test'))
    """
    return [{'type': attr_type, 'value': value} for attr_type, value in type_value_pairs]


def duplicate_attribute(attr_type: str, value: str, count: int = 2) -> list[dict[str, str]]:
    """Build a list of N identical attributes.

    Args:
        attr_type: The attribute type name.
        value: The attribute value.
        count: Number of copies to create.

    Returns:
        A list of identical attribute dicts.
    """
    return [{'type': attr_type, 'value': value} for _ in range(count)]


def tag_names(item: dict[str, Any]) -> set[str]:
    """Extract tag names from an item.

    Args:
        item: An indicator or group dict.

    Returns:
        A set of tag name strings.
    """
    return {tag['name'] for tag in item.get('tag', [])}


def label_names(item: dict[str, Any]) -> set[str]:
    """Extract security label names from an item.

    Args:
        item: An indicator or group dict.

    Returns:
        A set of security label name strings.
    """
    return {label['name'] for label in item.get('securityLabel', [])}


def count_log_warnings(
    caplog: pytest.LogCaptureFixture, keyword: str = 'attribute-truncated'
) -> int:
    """Count log records containing a keyword.

    Args:
        caplog: Pytest log capture fixture instance.
        keyword: Substring to search for in log messages.

    Returns:
        The number of matching log records.
    """
    return sum(1 for record in caplog.records if keyword in record.message)


def _make_cleaner(**kwargs: Any) -> BatchCleaner:
    """Create a BatchCleaner with noop defaults and the given flags.

    Args:
        **kwargs: Keyword arguments forwarded to the ``BatchCleaner`` constructor.

    Returns:
        A configured ``BatchCleaner`` instance.
    """
    kwargs.setdefault('attribute_types', {})
    kwargs.setdefault('mitre_tags', _noop_mitre_tags())
    return BatchCleaner(**kwargs)


def cleaner_with_all_flags(
    attribute_types: dict[str, dict] | None = None,
    mitre_tags: Any = None,
) -> BatchCleaner:
    """Create a BatchCleaner with every flag enabled.

    Args:
        attribute_types: Attribute type config dict keyed by name.
        mitre_tags: A MitreTags instance or mock.

    Returns:
        A ``BatchCleaner`` instance with all cleaning flags set to ``True``.
    """
    return BatchCleaner(
        attribute_types=attribute_types or {},
        mitre_tags=mitre_tags or _noop_mitre_tags(),
        combine_on_filename=True,
        convert_to_mitre_tags=True,
        convert_to_naics_tags=True,
        deduplicate_indicators=True,
        deduplicate_groups=True,
        deduplicate_attributes=True,
        truncate_attributes=True,
    )


# ---------------------------------------------------------------------------
# auto_truncate_attribute
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'value, max_size, expected',
    [
        ('short', 100, 'short'),
        ('exact len!', 10, 'exact len!'),
        ('this is way too long', 10, 'this is...'),
        ('abcdef', 2, 'ab'),
        ('abcdef', 3, 'abc'),
        ('abcdef', 4, 'a...'),
    ],
    ids=[
        'within-limit',
        'at-limit',
        'over-limit',
        'max-below-ellipsis-length',
        'max-equals-ellipsis-length',
        'max-just-above-ellipsis-length',
    ],
)
def test_auto_truncate(value: str, max_size: int, expected: str) -> None:
    """Verify auto_truncate_attribute truncates or preserves values correctly.

    Args:
        value: The attribute value to truncate.
        max_size: The maximum allowed length.
        expected: The expected result after truncation.
    """
    config = {'TestAttr': {'maxSize': max_size}}
    assert BatchCleaner.auto_truncate_attribute('TestAttr', value, config) == expected


@pytest.mark.parametrize(
    'config',
    [
        {},
        {'TestAttr': {'description': 'no maxSize key here'}},
        {'TestAttr': {'maxSize': 0}},
    ],
    ids=['type-not-in-config', 'config-missing-maxSize', 'maxSize-is-zero'],
)
def test_auto_truncate_returns_original_when_not_applicable(config: dict) -> None:
    """Verify truncation is skipped when config is missing or inapplicable.

    Args:
        config: Attribute type config that should not trigger truncation.
    """
    assert BatchCleaner.auto_truncate_attribute('TestAttr', 'hello', config) == 'hello'


def test_auto_truncate_returns_non_string_as_is() -> None:
    """Verify non-string attribute values are returned unchanged."""
    config = {'TestAttr': {'maxSize': 5}}
    assert BatchCleaner.auto_truncate_attribute('TestAttr', 12345, config) == 12345  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# combine_file_hashes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'existing, new, expected',
    [
        (MD5, SHA256, f'{MD5} : {SHA256}'),
        (f'{MD5} : {SHA1}', SHA256, f'{MD5} : {SHA1} : {SHA256}'),
        (SHA256, f'{SHA1} : {MD5}', f'{MD5} : {SHA1} : {SHA256}'),
        (MD5, MD5_ALT, MD5),
        ('short', MD5, MD5),
        (MD5, '', MD5),
        ('', '', ''),
        (
            f'{MD5} : {SHA1} : {SHA256}',
            f'{MD5_ALT} : {SHA1} : {SHA256}',
            f'{MD5} : {SHA1} : {SHA256}'
        ),
    ],
    ids=[
        'md5-plus-sha256',
        'all-three-hashes',
        'reorders-to-canonical-order',
        'same-hash-type-existing-wins',
        'ignores-invalid-length',
        'empty-new-summary',
        'both-empty',
        'overlapping-hashes',
    ],
)
def test_combine_file_hashes(existing: str, new: str, expected: str) -> None:
    """Verify combine_file_hashes produces the correct canonical summary.

    Args:
        existing: The existing File indicator summary.
        new: The new summary to merge in.
        expected: The expected combined summary.
    """
    assert BatchCleaner.combine_file_hashes(existing, new) == expected


# ---------------------------------------------------------------------------
# _file_hash_set
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'summary, expected',
    [
        (MD5, {MD5}),
        (f'{MD5} : {SHA1} : {SHA256}', {MD5, SHA1, SHA256}),
        ('', set()),
        (f'{SHA1} : {MD5} : {SHA256}', {MD5, SHA1, SHA256}),
    ],
    ids=['single-hash', 'three-hashes', 'empty-string', 'unordered-hashes'],
)
def test_file_hash_set(summary: str, expected: set[str]) -> None:
    """Verify _file_hash_set extracts individual hashes from a summary string.

    Args:
        summary: A File indicator summary string.
        expected: The expected set of extracted hash strings.
    """
    assert BatchCleaner._file_hash_set(summary) == expected


# ---------------------------------------------------------------------------
# clean_attributes - deduplication
# ---------------------------------------------------------------------------

def test_clean_attributes_removes_exact_duplicates() -> None:
    """Verify exact duplicate attributes are collapsed to a single entry."""
    item = {
        'attribute': duplicate_attribute('Description', 'duplicate value')
        + make_attributes(('Description', 'unique value'))
    }
    BatchCleaner.clean_attributes(item, {}, deduplicate=True, truncate=False)
    assert len(item['attribute']) == 2


def test_clean_attributes_keeps_attrs_with_different_extra_fields() -> None:
    """Verify attributes with same type/value but different extra fields are kept.

    Same type and value but different ``source`` field should not be treated as
    duplicates.
    """
    item = {'attribute': [
        {'type': 'Description', 'value': 'same value', 'source': 'SourceA'},
        {'type': 'Description', 'value': 'same value', 'source': 'SourceB'},
    ]}
    BatchCleaner.clean_attributes(item, {}, deduplicate=True, truncate=False)
    assert len(item['attribute']) == 2


# ---------------------------------------------------------------------------
# clean_attributes - filtering invalid entries
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'bad_attribute',
    [
        {'type': 'Description', 'value': None},
        {'type': 'Description', 'value': ''},
        {'value': 'missing type field'},
    ],
    ids=['none-value', 'empty-value', 'missing-type'],
)
def test_clean_attributes_skips_invalid_entries(bad_attribute: dict[str, Any]) -> None:
    """Verify invalid attribute entries are filtered out during cleaning.

    Args:
        bad_attribute: An attribute dict with a missing or empty required field.
    """
    item = {'attribute': [bad_attribute, {'type': 'Description', 'value': 'valid'}]}
    BatchCleaner.clean_attributes(item, {}, deduplicate=False, truncate=False)
    assert len(item['attribute']) == 1
    assert item['attribute'][0]['value'] == 'valid'


# ---------------------------------------------------------------------------
# clean_attributes - truncation
# ---------------------------------------------------------------------------

def test_clean_attributes_truncates_long_values() -> None:
    """Verify attribute values exceeding maxSize are truncated with ellipsis."""
    item = {'attribute': make_attributes(('Source', 'a' * 50))}
    BatchCleaner.clean_attributes(item, ATTRIBUTE_CONFIG, deduplicate=False, truncate=True)
    assert len(item['attribute'][0]['value']) == 20
    assert item['attribute'][0]['value'].endswith('...')


def test_clean_attributes_deduplicates_after_truncation() -> None:
    """Verify two different values that truncate to the same string become one."""
    item = {'attribute': [
        {'type': 'Source', 'value': 'common prefix - AAAA'},
        {'type': 'Source', 'value': 'common prefix - BBBB'},
    ]}
    BatchCleaner.clean_attributes(
        item, {'Source': {'maxSize': 15}}, deduplicate=True, truncate=True,
    )
    assert len(item['attribute']) == 1


# ---------------------------------------------------------------------------
# clean_attributes - edge cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'item',
    [
        {'summary': '1.2.3.4'},
        {'attribute': []},
        {'attribute': None},
    ],
    ids=['no-attribute-key', 'empty-list', 'none-value'],
)
def test_clean_attributes_handles_missing_or_empty(item: dict[str, Any]) -> None:
    """Verify clean_attributes gracefully handles missing or empty attribute lists.

    Args:
        item: An indicator/group dict with absent, empty, or ``None`` attributes.
    """
    result = BatchCleaner.clean_attributes(item, {})
    assert result is item
    assert result['attribute'] == []


# ---------------------------------------------------------------------------
# clean_attributes - truncation warning suppression
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'truncated_types, expected_warning_count',
    [
        (set(), 1),
        (None, 2),
        ({'Source'}, 0),
    ],
    ids=[
        'shared-set-logs-once-per-type',
        'none-logs-every-truncation',
        'pre-populated-suppresses-all',
    ],
)
def test_clean_attributes_truncation_warning_behavior(
    truncated_types: set[str] | None,
    expected_warning_count: int,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify truncation warning logging respects the truncated_types set.

    Args:
        truncated_types: Pre-populated set controlling warning suppression.
        expected_warning_count: Number of truncation warnings expected.
        caplog: Pytest fixture that captures log output for assertion.
    """
    item = {'attribute': make_attributes(('Source', 'x' * 50), ('Source', 'y' * 50))}
    with caplog.at_level(logging.WARNING):
        BatchCleaner.clean_attributes(
            item, ATTRIBUTE_CONFIG, truncate=True, deduplicate=False,
            truncated_types=truncated_types,
        )
    assert count_log_warnings(caplog) == expected_warning_count


# ---------------------------------------------------------------------------
# merge_list_field
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'existing, incoming, expected_length',
    [
        ({'tag': [{'name': 'a'}]}, {'tag': [{'name': 'b'}]}, 2),
        ({'tag': [{'name': 'a'}]}, {'tag': [{'name': 'a'}, {'name': 'b'}]}, 2),
        ({}, {'tag': [{'name': 'x'}]}, 1),
        ({'tag': [{'name': 'a'}]}, {'tag': []}, 1),
        ({'tag': [{'name': 'a'}]}, {}, 1),
    ],
    ids=[
        'appends-new-item',
        'deduplicates-overlap',
        'creates-field-when-missing',
        'no-op-for-empty-incoming',
        'no-op-for-missing-incoming-field',
    ],
)
def test_merge_list_field_tag(
    existing: dict[str, Any], incoming: dict[str, Any], expected_length: int
) -> None:
    """Verify merge_list_field correctly merges tag lists.

    Args:
        existing: The target dict to merge into.
        incoming: The source dict to merge from.
        expected_length: Expected number of tags after merge.
    """
    BatchCleaner.merge_list_field(existing, incoming, 'tag')
    assert len(existing.get('tag', [])) == expected_length


@pytest.mark.parametrize(
    'existing, incoming, expected_length',
    [
        (
            {'attribute': [{'type': 'Description', 'value': 'test'}]},
            {'attribute': [{'type': 'Description', 'value': 'test'}, {'type': 'Description', 'value': 'test', 'source': 'src'}]},
            2
        ),
    ],
    ids=[
        'different-attributes-not-deduped',
    ],
)
def test_merge_list_field_attribute(
    existing: dict[str, Any], incoming: dict[str, Any], expected_length: int
) -> None:
    """Verify merge_list_field correctly merges attribute lists.

    Args:
        existing: The target dict to merge into.
        incoming: The source dict to merge from.
        expected_length: Expected number of attributes after merge.
    """
    BatchCleaner.merge_list_field(existing, incoming, 'attribute')
    assert len(existing.get('attribute', [])) == expected_length


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('field', ['tag', 'securityLabel', 'associatedGroups'])
def test_deduplicate_merges_list_fields(field: str) -> None:
    """Verify deduplicate merges tag, securityLabel, and associatedGroups lists.

    Args:
        field: The list field name to test merging on.
    """
    existing = make_indicator('1.2.3.4', **{field: [{'name': 'a'}]})  # type: ignore[arg-type]
    incoming = make_indicator('1.2.3.4', **{field: [{'name': 'b'}]})  # type: ignore[arg-type]
    cleaner = cleaner_with_all_flags()
    result = cleaner.deduplicate(incoming, existing)
    assert result is existing
    assert len(existing[field]) == 2


def test_deduplicate_concatenates_attributes() -> None:
    """Verify deduplicate appends attributes from incoming into existing."""
    existing = make_indicator('1.2.3.4', attribute=make_attributes(('TypeA', 'val1')))
    incoming = make_indicator('1.2.3.4', attribute=make_attributes(('TypeB', 'val2')))
    cleaner = cleaner_with_all_flags()
    cleaner.deduplicate(incoming, existing)
    assert len(existing['attribute']) == 2


def test_deduplicate_merges_file_hashes() -> None:
    """Verify deduplicate combines File indicator hash summaries."""
    existing = make_file_indicator(MD5)
    incoming = make_file_indicator(SHA256)
    cleaner = cleaner_with_all_flags()
    cleaner.deduplicate(incoming, existing)
    assert existing['summary'] == f'{MD5} : {SHA256}'


def test_deduplicate_does_not_change_non_file_summary() -> None:
    """Verify deduplicate leaves non-File indicator summaries unchanged."""
    existing = make_indicator('1.2.3.4')
    cleaner = cleaner_with_all_flags()
    cleaner.deduplicate(make_indicator('5.6.7.8'), existing)
    assert existing['summary'] == '1.2.3.4'


# ---------------------------------------------------------------------------
# clean() - indicator deduplication
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'deduplicate, indicators, expected_count',
    [
        (True, [make_indicator('1.2.3.4'), make_indicator('1.2.3.4')], 1),
        (True, [make_indicator('1.2.3.4'), make_indicator('5.6.7.8')], 2),
        (False, [make_indicator('1.2.3.4'), make_indicator('1.2.3.4')], 2),
        (True, [make_indicator(None), make_indicator(None)], 2),
        (True, [make_file_indicator(MD5), make_file_indicator(f'{MD5} : {SHA256}')], 1),
        (True, [make_file_indicator(MD5), make_file_indicator(SHA256)], 2),
    ],
    ids=[
        'same-summary-merged',
        'different-summary-kept-separate',
        'disabled-keeps-duplicates',
        'null-summary-not-deduplicated',
        'file-hash-overlap-merged',
        'file-no-overlap-kept-separate',
    ],
)
def test_clean_indicator_dedup(
    deduplicate: bool, indicators: list[dict[str, Any]], expected_count: int
) -> None:
    """Verify indicator deduplication behavior under various conditions.

    Args:
        deduplicate: Whether the deduplicate_indicators flag is enabled.
        indicators: List of indicators to clean.
        expected_count: Expected number of indicators after cleaning.
    """
    cleaner = _make_cleaner(deduplicate_indicators=deduplicate)
    result = cleaner.clean(make_content(indicators=indicators))
    assert len(result['indicator']) == expected_count


def test_clean_indicator_chain_merge() -> None:
    """Verify three File indicators linked by overlapping hashes all merge into one."""
    cleaner = _make_cleaner(deduplicate_indicators=True)
    result = cleaner.clean(make_content(indicators=[
        make_file_indicator(MD5, tag=[{'name': 'a'}]),
        make_file_indicator(f'{MD5} : {SHA1}', tag=[{'name': 'b'}]),
        make_file_indicator(SHA1, tag=[{'name': 'c'}]),
    ]))
    assert len(result['indicator']) == 1
    assert tag_names(result['indicator'][0]) == {'a', 'b', 'c'}


def test_clean_indicator_merge_combines_tags_and_labels() -> None:
    """Verify merged indicators combine tags and security labels."""
    cleaner = _make_cleaner(deduplicate_indicators=True)
    result = cleaner.clean(make_content(indicators=[
        make_indicator(
            '1.2.3.4',
            tag=[{'name': 'tag1'}],
            securityLabel=[{'name': 'TLP:RED'}],
        ),
        make_indicator(
            '1.2.3.4',
            tag=[{'name': 'tag2'}],
            securityLabel=[{'name': 'TLP:RED'}, {'name': 'TLP:GREEN'}],
        ),
    ]))
    merged = result['indicator'][0]
    assert tag_names(merged) == {'tag1', 'tag2'}
    assert label_names(merged) == {'TLP:RED', 'TLP:GREEN'}


# ---------------------------------------------------------------------------
# clean() - combine on filename
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'filename_a, filename_b, expected_count',
    [
        ('malware.exe', 'malware.exe', 1),
        ('Malware.EXE', 'malware.exe', 1),
        ('a.exe', 'b.exe', 2),
    ],
    ids=['exact-match', 'case-insensitive-match', 'different-filenames'],
)
def test_clean_combine_on_filename(
    filename_a: str, filename_b: str, expected_count: int
) -> None:
    """Verify File indicators are combined when they share a fileOccurrence filename.

    Args:
        filename_a: Filename for the first indicator's fileOccurrence.
        filename_b: Filename for the second indicator's fileOccurrence.
        expected_count: Expected number of indicators after cleaning.
    """
    cleaner = _make_cleaner(combine_on_filename=True)
    result = cleaner.clean(make_content(indicators=[
        make_file_indicator(MD5, filename=filename_a),
        make_file_indicator(SHA256, filename=filename_b),
    ]))
    assert len(result['indicator']) == expected_count


def test_clean_combine_on_filename_merges_hashes() -> None:
    """Verify filename-combined indicators have their hash summaries merged."""
    cleaner = _make_cleaner(combine_on_filename=True)
    result = cleaner.clean(make_content(indicators=[
        make_file_indicator(MD5, filename='test.exe'),
        make_file_indicator(SHA256, filename='test.exe'),
    ]))
    summary = result['indicator'][0]['summary']
    assert MD5 in summary and SHA256 in summary


def test_clean_combine_on_filename_requires_file_occurrence() -> None:
    """Verify File indicators without fileOccurrence are not combined by filename."""
    cleaner = _make_cleaner(combine_on_filename=True)
    result = cleaner.clean(make_content(indicators=[
        make_file_indicator(MD5),
        make_file_indicator(SHA256),
    ]))
    assert len(result['indicator']) == 2


def test_clean_combine_on_filename_ignores_non_file_indicators() -> None:
    """Verify non-File indicators are not affected by combine_on_filename."""
    cleaner = _make_cleaner(combine_on_filename=True)
    result = cleaner.clean(make_content(indicators=[
        make_indicator('1.2.3.4'),
        make_indicator('1.2.3.4'),
    ]))
    assert len(result['indicator']) == 2


def test_clean_combine_on_filename_works_with_hash_dedup() -> None:
    """Verify both flags work together: filename match and hash overlap both trigger merges."""
    cleaner = _make_cleaner(deduplicate_indicators=True, combine_on_filename=True)
    result = cleaner.clean(make_content(indicators=[
        make_file_indicator(MD5, filename='a.exe'),
        make_file_indicator(MD5),
        make_file_indicator(SHA256, filename='a.exe'),
    ]))
    assert len(result['indicator']) == 1


# ---------------------------------------------------------------------------
# clean() - group deduplication
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'deduplicate, groups, expected_count',
    [
        (True, [make_group('G', xid='x1'), make_group('G', xid='x1')], 1),
        (True, [make_group('G', xid='x1'), make_group('G', xid='x2')], 2),
        (True, [make_group('G'), make_group('G')], 2),
        (False, [make_group('G', xid='x1'), make_group('G', xid='x1')], 2),
    ],
    ids=['same-xid-merged', 'different-xid-kept', 'no-xid-not-deduplicated', 'disabled'],
)
def test_clean_group_dedup(
    deduplicate: bool, groups: list[dict[str, Any]], expected_count: int
) -> None:
    """Verify group deduplication behavior based on xid matching.

    Args:
        deduplicate: Whether the deduplicate_groups flag is enabled.
        groups: List of groups to clean.
        expected_count: Expected number of groups after cleaning.
    """
    cleaner = _make_cleaner(deduplicate_groups=deduplicate)
    result = cleaner.clean(make_content(groups=groups))
    assert len(result['group']) == expected_count


def test_clean_group_merge_combines_tags() -> None:
    """Verify merged groups combine their tag lists."""
    cleaner = _make_cleaner(deduplicate_groups=True)
    result = cleaner.clean(make_content(groups=[
        make_group('G', xid='x1', tag=[{'name': 'a'}]),
        make_group('G', xid='x1', tag=[{'name': 'b'}]),
    ]))
    assert tag_names(result['group'][0]) == {'a', 'b'}


# ---------------------------------------------------------------------------
# clean() - full pipeline integration
# ---------------------------------------------------------------------------

def test_clean_accepts_json_string() -> None:
    """Verify clean() accepts a JSON string and returns a parsed dict."""
    content = make_content(indicators=[
        make_indicator('1.2.3.4', attribute=duplicate_attribute('Description', 'dup')),
        make_indicator('1.2.3.4', attribute=make_attributes(('Description', 'other'))),
    ])
    cleaner = _make_cleaner(deduplicate_indicators=True, deduplicate_attributes=True)
    result = cleaner.clean(json.dumps(content))
    assert len(result['indicator']) == 1
    assert len(result['indicator'][0]['attribute']) == 2


def test_clean_no_flags_is_passthrough() -> None:
    """Verify clean() with no flags enabled passes content through unchanged."""
    content = make_content(
        indicators=[make_indicator('1.2.3.4'), make_indicator('1.2.3.4')],
        groups=[make_group('G', xid='x'), make_group('G', xid='x')],
    )
    result = _make_cleaner().clean(content)
    assert len(result['indicator']) == 2
    assert len(result['group']) == 2


def test_clean_handles_empty_content() -> None:
    """Verify clean() handles content with no indicators or groups."""
    result = cleaner_with_all_flags().clean(make_content())
    assert result['indicator'] == []
    assert result['group'] == []


def test_clean_skips_truncation_when_no_attribute_config() -> None:
    """Verify truncation is a no-op when attribute_types is empty."""
    content = make_content(indicators=[
        make_indicator('1.2.3.4', attribute=make_attributes(('Source', 'x' * 50))),
    ])
    cleaner = _make_cleaner(truncate_attributes=True)
    result = cleaner.clean(content)
    assert result['indicator'][0]['attribute'][0]['value'] == 'x' * 50


def test_clean_deduplicates_group_attributes() -> None:
    """Verify attribute deduplication works on group items."""
    content = make_content(groups=[
        make_group('G', attribute=duplicate_attribute('Description', 'dup')),
    ])
    result = _make_cleaner(deduplicate_attributes=True).clean(content)
    assert len(result['group'][0]['attribute']) == 1


def test_clean_strips_empty_and_none_attribute_values() -> None:
    """Verify attributes with empty or None values are removed during cleaning."""
    content = make_content(indicators=[make_indicator('1.2.3.4', attribute=[
        {'type': 'Events', 'value': 'Valid'},
        {'type': 'Events', 'value': ''},
        {'type': 'Events', 'value': None},
    ])])
    result = _make_cleaner(deduplicate_attributes=True).clean(content)
    assert len(result['indicator'][0]['attribute']) == 1


def test_clean_preserves_unique_attributes() -> None:
    """Verify unique attributes are preserved during deduplication."""
    content = make_content(indicators=[make_indicator('1.2.3.4', attribute=make_attributes(
        ('Events', 'First'), ('Events', 'Second'), ('Description', 'Third'),
    ))])
    result = _make_cleaner(deduplicate_attributes=True).clean(content)
    assert len(result['indicator'][0]['attribute']) == 3


def test_clean_full_pipeline_with_all_flags() -> None:
    """Verify all flags together: filename combine, hash merge, attribute truncation and dedup."""
    content = make_content(
        indicators=[
            make_file_indicator(
                MD5, filename='test.exe',
                attribute=duplicate_attribute('Source', 'x' * 50),
            ),
            make_file_indicator(
                SHA256, filename='test.exe',
                attribute=make_attributes(('Description', 'desc')),
            ),
        ],
        groups=[
            make_group('G', xid='x1', attribute=duplicate_attribute('Description', 'dup')),
            make_group('G', xid='x1'),
        ],
    )
    result = cleaner_with_all_flags(
        attribute_types=ATTRIBUTE_CONFIG,
    ).clean(content)

    # indicators merged by filename, hashes combined
    assert len(result['indicator']) == 1
    indicator = result['indicator'][0]
    assert MD5 in indicator['summary'] and SHA256 in indicator['summary']

    source_attrs = [a for a in indicator['attribute'] if a['type'] == 'Source']
    assert len(source_attrs) == 1
    assert len(source_attrs[0]['value']) == 20

    # groups merged by xid, attributes deduped
    assert len(result['group']) == 1
    assert len(result['group'][0]['attribute']) == 1


def test_clean_logs_truncation_warning_once_per_attribute_type(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify the shared truncated_types set limits warnings to one per type across all items.

    Args:
        caplog: Pytest fixture that captures log output for assertion.
    """
    content = make_content(
        indicators=[
            make_indicator('1.2.3.4', attribute=make_attributes(('Source', 'x' * 50))),
            make_indicator('5.6.7.8', attribute=make_attributes(('Source', 'y' * 50))),
        ],
        groups=[
            make_group('G', attribute=make_attributes(('Source', 'z' * 50))),
        ],
    )
    with caplog.at_level(logging.WARNING):
        _make_cleaner(
            attribute_types=ATTRIBUTE_CONFIG,
            truncate_attributes=True,
        ).clean(content)
    assert count_log_warnings(caplog) == 1


# ---------------------------------------------------------------------------
# Constructor defaults
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('field', [
    'deduplicate_indicators',
    'deduplicate_groups',
    'deduplicate_attributes',
    'truncate_attributes',
    'combine_on_filename',
    'convert_to_mitre_tags',
    'convert_to_naics_tags',
])
def test_all_flags_default_to_false(field: str) -> None:
    """Verify all BatchCleaner boolean flags default to False.

    Args:
        field: The flag attribute name to check.
    """
    assert getattr(_make_cleaner(), field) is False


def test_all_flags_enabled() -> None:
    """Verify cleaner_with_all_flags sets every boolean flag to True."""
    cleaner = cleaner_with_all_flags()
    assert cleaner.deduplicate_indicators is True
    assert cleaner.deduplicate_groups is True
    assert cleaner.deduplicate_attributes is True
    assert cleaner.truncate_attributes is True
    assert cleaner.combine_on_filename is True
    assert cleaner.convert_to_mitre_tags is True
    assert cleaner.convert_to_naics_tags is True


def test_selective_flag_enable() -> None:
    """Verify only explicitly enabled flags are True."""
    cleaner = _make_cleaner(deduplicate_indicators=True, truncate_attributes=True)
    assert cleaner.deduplicate_indicators is True
    assert cleaner.truncate_attributes is True
    assert cleaner.deduplicate_groups is False


# ---------------------------------------------------------------------------
# deduplicate() - rating/confidence max logic
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    'existing_val, incoming_val, expected',
    [
        (3, 5, 5),
        (5, 3, 5),
        (0, 5, 5),
        (5, 0, 5),
    ],
    ids=['incoming-higher', 'existing-higher', 'existing-zero', 'incoming-zero'],
)
@pytest.mark.parametrize('field', ['rating', 'confidence'])
def test_deduplicate_keeps_highest_value(
    field: str, existing_val: int, incoming_val: int, expected: int
) -> None:
    """Verify deduplicate keeps the higher rating/confidence value.

    Args:
        field: The field name ('rating' or 'confidence').
        existing_val: The value on the existing item.
        incoming_val: The value on the incoming item.
        expected: The expected value after merge.
    """
    existing = make_indicator('1.2.3.4', **{field: existing_val}) # type: ignore
    incoming = make_indicator('1.2.3.4', **{field: incoming_val}) # type: ignore
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing[field] == expected


def test_deduplicate_adopts_incoming_rating_when_existing_has_none() -> None:
    """Verify incoming rating is adopted when existing has no rating field."""
    existing = make_indicator('1.2.3.4')
    incoming = make_indicator('1.2.3.4', rating=5)
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing['rating'] == 5


def test_deduplicate_preserves_existing_rating_when_incoming_has_none() -> None:
    """Verify existing rating is preserved when incoming has no rating field."""
    existing = make_indicator('1.2.3.4', rating=5)
    incoming = make_indicator('1.2.3.4')
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing['rating'] == 5


# ---------------------------------------------------------------------------
# deduplicate() - date merging (earliest/latest)
# ---------------------------------------------------------------------------

def test_deduplicate_keeps_earliest_external_date_added() -> None:
    """Verify externalDateAdded resolves to the earlier of the two dates."""
    existing = make_indicator('1.2.3.4', externalDateAdded='2024-03-01T00:00:00Z')
    incoming = make_indicator('1.2.3.4', externalDateAdded='2024-01-15T00:00:00Z')
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing['externalDateAdded'] == '2024-01-15T00:00:00Z'


def test_deduplicate_keeps_existing_when_earlier_date_added() -> None:
    """Verify externalDateAdded keeps existing when it is already earlier."""
    existing = make_indicator('1.2.3.4', externalDateAdded='2024-01-15T00:00:00Z')
    incoming = make_indicator('1.2.3.4', externalDateAdded='2024-03-01T00:00:00Z')
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing['externalDateAdded'] == '2024-01-15T00:00:00Z'


def test_deduplicate_keeps_latest_external_date_last_modified() -> None:
    """Verify externalDateLastModified resolves to the later of the two dates."""
    existing = make_indicator('1.2.3.4', externalDateLastModified='2024-01-15T00:00:00Z')
    incoming = make_indicator('1.2.3.4', externalDateLastModified='2024-03-01T00:00:00Z')
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing['externalDateLastModified'] == '2024-03-01T00:00:00Z'


def test_deduplicate_keeps_existing_when_later_date_last_modified() -> None:
    """Verify externalDateLastModified keeps existing when it is already later."""
    existing = make_indicator('1.2.3.4', externalDateLastModified='2024-03-01T00:00:00Z')
    incoming = make_indicator('1.2.3.4', externalDateLastModified='2024-01-15T00:00:00Z')
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing['externalDateLastModified'] == '2024-03-01T00:00:00Z'


def test_deduplicate_adopts_incoming_date_when_existing_missing() -> None:
    """Verify incoming externalDateAdded is adopted when existing has none."""
    existing = make_indicator('1.2.3.4')
    incoming = make_indicator('1.2.3.4', externalDateAdded='2024-06-01T00:00:00Z')
    cleaner = _make_cleaner(deduplicate_indicators=True)
    cleaner.deduplicate(incoming, existing)
    assert existing['externalDateAdded'] == '2024-06-01T00:00:00Z'


def test_deduplicate_logs_on_invalid_date(caplog: pytest.LogCaptureFixture) -> None:
    """Verify invalid date values are caught and logged without raising."""
    existing = make_indicator('1.2.3.4', externalDateAdded='not-a-date')
    incoming = make_indicator('1.2.3.4', externalDateAdded='also-not-a-date')
    cleaner = _make_cleaner(deduplicate_indicators=True)
    with caplog.at_level(logging.ERROR):
        cleaner.deduplicate(incoming, existing)
    assert any('Invalid date' in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# _normalize_tags
# ---------------------------------------------------------------------------

MITRE_TAG_DATA: dict[str, str] = {'T1059': 'Command and Scripting Interpreter'}


def test_normalize_tags_converts_mitre_id() -> None:
    """Verify a MITRE technique ID tag is converted to formatted MITRE tag name."""
    cleaner = _make_cleaner(
        mitre_tags=_mock_mitre_tags(MITRE_TAG_DATA),
        convert_to_mitre_tags=True,
    )
    tags = [{'name': 'T1059'}]
    cleaner._normalize_tags(tags)
    assert tags[0]['name'] == 'T1059 - Command and Scripting Interpreter'


def test_normalize_tags_converts_naics_id() -> None:
    """Verify a NAICS ID tag is converted to formatted NAICS tag name."""
    cleaner = _make_cleaner(convert_to_naics_tags=True)
    tags = [{'name': '11'}]
    cleaner._normalize_tags(tags)
    assert tags[0]['name'] == 'NAICS: 11 - Agriculture, Forestry, Fishing and Hunting'


def test_normalize_tags_leaves_unmatched_unchanged() -> None:
    """Verify tags that match neither MITRE nor NAICS are left unchanged."""
    cleaner = _make_cleaner(
        mitre_tags=_mock_mitre_tags(MITRE_TAG_DATA),
        convert_to_mitre_tags=True,
        convert_to_naics_tags=True,
    )
    tags = [{'name': 'UnknownTag'}]
    cleaner._normalize_tags(tags)
    assert tags[0]['name'] == 'UnknownTag'


def test_normalize_tags_skips_empty_name() -> None:
    """Verify tags with empty or missing names are skipped without error."""
    cleaner = _make_cleaner(
        mitre_tags=_mock_mitre_tags(MITRE_TAG_DATA),
        convert_to_mitre_tags=True,
        convert_to_naics_tags=True,
    )
    tags: list[dict[str, Any]] = [{'name': ''}, {'name': None}, {}]
    cleaner._normalize_tags(tags)
    assert tags[0].get('name') == ''
    assert tags[1].get('name') is None
    assert 'name' not in tags[2]


def test_normalize_tags_mitre_takes_priority_over_naics() -> None:
    """Verify MITRE conversion is checked first and short-circuits NAICS."""
    cleaner = _make_cleaner(
        mitre_tags=_mock_mitre_tags(MITRE_TAG_DATA),
        convert_to_mitre_tags=True,
        convert_to_naics_tags=True,
    )
    tags = [{'name': 'T1059'}]
    cleaner._normalize_tags(tags)
    assert tags[0]['name'].startswith('T1059 - ')


def test_normalize_tags_only_naics_when_mitre_disabled() -> None:
    """Verify NAICS conversion applies when only NAICS flag is enabled."""
    cleaner = _make_cleaner(convert_to_naics_tags=True)
    tags = [{'name': '11'}]
    cleaner._normalize_tags(tags)
    assert tags[0]['name'] == 'NAICS: 11 - Agriculture, Forestry, Fishing and Hunting'


def test_normalize_tags_noop_when_both_flags_disabled() -> None:
    """Verify no conversion occurs when both MITRE and NAICS flags are disabled."""
    cleaner = _make_cleaner()
    tags = [{'name': 'T1059'}, {'name': '11'}]
    cleaner._normalize_tags(tags)
    assert tags[0]['name'] == 'T1059'
    assert tags[1]['name'] == '11'


# ---------------------------------------------------------------------------
# E2E - batch_data.json
# ---------------------------------------------------------------------------

def test_e2e_batch_data_json(tcex: TcEx) -> None:
    """Load batch_data.json and run it through the cleaner with all flags enabled.

    Args:
        tcex: Pytest fixture providing a configured TcEx instance.
    """
    batch = tcex.api.tc.v2.batch(owner='TCI')

    data_path = Path(__file__).parent / 'batch_data.json'
    content = json.loads(data_path.read_text())
    cleaner = batch.cleaner(
        combine_on_filename=True,
        convert_to_mitre_tags=True,
        convert_to_naics_tags=True,
        deduplicate_indicators=True,
        deduplicate_groups=True,
        deduplicate_attributes=True,
        truncate_attributes=True,
    )
    cleaner.clean(content)

    # load expected cleaned content
    expected_path = Path(__file__).parent / 'batch_data_cleaned.json'
    # expected_path.write_text(json.dumps(content, indent=2))
    expected_content = json.loads(expected_path.read_text())
    ddiff = DeepDiff(content, expected_content, ignore_order=True)
    assert not ddiff, ddiff

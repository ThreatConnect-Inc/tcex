"""TcEx Framework Module"""

import json
import logging
from collections.abc import Callable
from itertools import chain

from tcex.api.tc.v3.tags.mitre_tags import MitreTags
from tcex.api.tc.v3.tags.naics_tags import NAICSTags
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property
from tcex.util.datetime_operation import DatetimeOperation

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class BatchCleaner:
    """Batch content cleaning configuration and logic.

    All flags default to False. Enable the desired cleaning steps before calling clean().
    """

    def __init__(
        self,
        attribute_types: dict[str, dict],
        mitre_tags: MitreTags,
        *,
        combine_on_filename: bool = False,
        convert_to_mitre_tags: bool = False,
        convert_to_naics_tags: bool = False,
        deduplicate_indicators: bool = False,
        deduplicate_groups: bool = False,
        deduplicate_attributes: bool = False,
        truncate_attributes: bool = False,
    ):
        """Initialize instance properties.

        Args:
            attribute_types: A dictionary of attribute type config.
            mitre_tags: A MitreTags instance.
            combine_on_filename: Whether to combine items based on filename.
            convert_to_mitre_tags: Whether to convert Mitre tags.
            convert_to_naics_tags: Whether to convert NAICS tags.
            deduplicate_indicators: Whether to deduplicate indicators.
            deduplicate_groups: Whether to deduplicate groups.
            deduplicate_attributes: Whether to deduplicate attributes.
            truncate_attributes: Whether to truncate attributes.
        """
        self.attribute_types = attribute_types
        self.mitre_tags = mitre_tags

        self.combine_on_filename = combine_on_filename
        self.convert_to_mitre_tags = convert_to_mitre_tags
        self.convert_to_naics_tags = convert_to_naics_tags
        self.deduplicate_indicators = deduplicate_indicators
        self.deduplicate_groups = deduplicate_groups
        self.deduplicate_attributes = deduplicate_attributes
        self.truncate_attributes = truncate_attributes

    def clean(self, content: dict | str) -> dict:
        """Run enabled cleaning steps on content.

        Pass 1: Deduplicate and combine indicators/groups.
        Pass 2: Clean attributes (truncate/deduplicate) on the result.

        Args:
            content: The batch content dictionary or JSON string.

        Returns:
            The cleaned content dictionary.
        """
        content_dict = json.loads(content) if isinstance(content, str) else content

        # Pass 1: dedup/combine
        content_dict['indicator'] = self._dedup_indicators(content_dict.get('indicator', []))
        if self.deduplicate_groups:
            content_dict['group'] = self._dedup(content_dict.get('group', []), self._group_keys)

        # Pass 2: attribute cleaning
        if self.deduplicate_attributes or self.truncate_attributes:
            truncated_types: set[str] = set()
            for item in chain(
                content_dict.get('indicator') or [],
                content_dict.get('group') or [],
            ):
                self.clean_attributes(
                    item,
                    self.attribute_types,
                    deduplicate=self.deduplicate_attributes,
                    truncate=self.truncate_attributes,
                    truncated_types=truncated_types,
                )

        return content_dict

    def _dedup_indicators(self, indicators: list[dict]) -> list[dict]:
        """Deduplicate and combine indicators.

        When deduplicate_indicators is enabled, indicators are matched by
        summary (hash-overlap for File indicators, exact match for others).

        When combine_on_filename is enabled, File indicators with matching
        fileOccurrence fileName values are also merged.

        Args:
            indicators: The list of indicator dictionaries.

        Returns:
            The deduplicated list of indicator dictionaries.
        """
        if not self.deduplicate_indicators and not self.combine_on_filename:
            return indicators

        return self._dedup(indicators, self._indicator_keys)

    def _dedup(
        self,
        items: list[dict],
        key_fn: Callable[[dict], set[str]],
    ) -> list[dict]:
        """Deduplicate items using a key function that returns a set of lookup keys.

        Each item is matched against previously seen keys. If any key from the
        incoming item is already in the index, the item is merged into the
        existing one. After a merge, keys are re-indexed to account for new
        keys added during the merge (e.g. File hash combination).

        Args:
            items: The list of items to deduplicate.
            key_fn: A callable that takes an item dict and returns a set of
                strings to use as lookup keys. Return an empty set for items
                that should never be deduplicated.

        Returns:
            The deduplicated list of items.
        """
        result: list[dict] = []
        seen: dict[str, int] = {}

        for item in items:
            keys = key_fn(item)
            match_idx = next((seen[k] for k in keys if k in seen), None)
            if match_idx is not None:
                self.deduplicate(item, result[match_idx])
                # re-index: merged item may have new keys (e.g. combined file hashes)
                for k in key_fn(result[match_idx]):
                    seen[k] = match_idx
            else:
                idx = len(result)
                for k in keys:
                    seen[k] = idx
                result.append(item)

        return result

    def _indicator_keys(self, item: dict) -> set[str]:
        """Return the set of dedup keys for an indicator.

        File indicators return individual hashes so that any hash overlap
        triggers a merge. When combine_on_filename is enabled, a prefixed
        filename key is also included for File indicators with a fileOccurrence.

        All other indicators return the summary as a single-element set.

        Args:
            item: An indicator dictionary.

        Returns:
            A set of key strings for dedup lookup.
        """
        if item.get('type') == 'File':
            keys: set[str] = set()
            if self.deduplicate_indicators:
                keys = BatchCleaner._file_hash_set(item.get('summary', ''))
            if self.combine_on_filename:
                file_occ = item.get('fileOccurrence') or []
                if file_occ:
                    fname = file_occ[0].get('fileName')
                    if fname:
                        keys.add(f'filename:{fname.lower()}')
            return keys
        if self.deduplicate_indicators:
            summary = item.get('summary')
            return {summary} if summary else set()
        return set()

    @staticmethod
    def _group_keys(item: dict) -> set[str]:
        """Return the set of dedup keys for a group.

        Groups are deduplicated by xid.

        Args:
            item: A group dictionary.

        Returns:
            A single-element set containing the xid, or empty set if no xid.
        """
        xid = item.get('xid')
        return {xid} if xid else set()

    def _normalize_tags(self, tags: list) -> None:
        """Convert tag names to formatted MITRE/NAICS format where applicable.

        Args:
            tags: A list of tags
        """
        for tag in tags:
            name = tag.get('name')
            if not name:
                continue

            # try MITRE conversion first
            if self.convert_to_mitre_tags:
                formatted = self.mitre_tags.get_by_id_regex(name)
                if formatted:
                    tag['name'] = formatted
                    continue

            # try NAICS conversion
            if self.convert_to_naics_tags:
                formatted = self.naics_tags.get_by_id(name)
                if formatted:
                    tag['name'] = formatted

    @staticmethod
    def auto_truncate_attribute(
        attribute_type: str,
        attribute_value: str,
        attribute_config: dict,
        ellipsis: str = '...',
    ) -> str:
        """Truncate attribute value if it exceeds the maximum length for its type.

        Args:
            attribute_type: The name of the attribute type.
            attribute_value: The attribute value to potentially truncate.
            attribute_config: Attribute type config dict keyed by name.
            ellipsis: The string to append when truncating. Defaults to '...'.

        Returns:
            The original value if within limits, or the truncated value with ellipsis.
        """
        config = attribute_config.get(attribute_type)
        if not config:
            return attribute_value

        max_length = config.get('maxSize')
        if not max_length:
            return attribute_value

        if not isinstance(attribute_value, str):
            return attribute_value

        if len(attribute_value) <= max_length:
            return attribute_value

        if max_length <= len(ellipsis):
            return attribute_value[:max_length]

        return attribute_value[: max_length - len(ellipsis)] + ellipsis

    @staticmethod
    def clean_attributes(
        item: dict,
        attribute_types: dict,
        deduplicate: bool = False,
        truncate: bool = False,
        truncated_types: set[str] | None = None,
    ) -> dict:
        """Truncate and/or deduplicate attributes on a single item.

        Args:
            item: A single group or indicator dictionary.
            attribute_types: Attribute type config dict keyed by name.
            deduplicate: Whether to remove duplicate attributes.
            truncate: Whether to truncate attributes based on maxSize.
            truncated_types: A shared set tracking attribute types that have already
                been logged as truncated, to avoid duplicate log warnings. If None,
                warnings are logged for every truncation.

        Returns:
            The item with cleaned attributes.
        """
        original_attrs = item.get('attribute') or []
        cleaned_attrs = []
        seen: set[tuple] = set()

        for attr in original_attrs:
            type_ = attr.get('type')
            value = attr.get('value')

            if not type_ or value is None or value == '':
                continue

            if truncate:
                truncated = BatchCleaner.auto_truncate_attribute(type_, value, attribute_types)
                if truncated != value and (truncated_types is None or type_ not in truncated_types):
                    _logger.warning(
                        f'feature=batch, event=attribute-truncated, attribute-type={type_}'
                    )
                    if truncated_types is not None:
                        truncated_types.add(type_)
            else:
                truncated = value

            if deduplicate:
                normalized = tuple(
                    (k, truncated if k == 'value' else attr.get(k)) for k in sorted(attr.keys())
                )
                if normalized in seen:
                    continue
                seen.add(normalized)

            new_attr = dict(attr)
            new_attr['value'] = truncated
            cleaned_attrs.append(new_attr)

        item['attribute'] = cleaned_attrs
        return item

    @staticmethod
    def merge_list_field(existing: dict, incoming: dict, field: str) -> None:
        """Merge a list-of-dicts field from incoming into existing, removing duplicates.

        Args:
            existing: The target item (modified in place).
            incoming: The source item to merge from.
            field: The field name (e.g. 'tag', 'securityLabel').
        """
        incoming_items = incoming.get(field) or []
        if not incoming_items:
            return

        existing_items = existing.setdefault(field, [])
        seen = {frozenset(item.items()) for item in existing_items}
        for item in incoming_items:
            key = frozenset(item.items())
            if key not in seen:
                seen.add(key)
                existing_items.append(item)

    def deduplicate(self, incoming: dict, existing: dict) -> dict:
        """Merge incoming item into existing.

        For File indicators, summaries are combined via hash merging.

        Args:
            incoming: The new item.
            existing: The previously seen item to merge into.

        Returns:
            The merged item (same reference as existing).
        """
        # merge File hash summaries
        if existing.get('type') == 'File' and incoming.get('type') == 'File':
            existing['summary'] = BatchCleaner.combine_file_hashes(
                existing.get('summary', ''), incoming.get('summary', '')
            )

        # merge associated group xids
        incoming_xids = incoming.get('associatedGroupXid') or []
        if incoming_xids:
            existing_xids = existing.get('associatedGroupXid') or []
            existing['associatedGroupXid'] = list(set(existing_xids + incoming_xids))

        # normalize existing tags
        existing_tags = existing.get('tag') or []
        if existing_tags:
            self._normalize_tags(existing_tags)

        # normalize incoming tags
        incoming_tags = incoming.get('tag') or []
        if incoming_tags:
            self._normalize_tags(incoming_tags)

        # merge metadata
        BatchCleaner.merge_list_field(existing, incoming, 'associatedGroups')
        BatchCleaner.merge_list_field(existing, incoming, 'fileOccurrence')
        BatchCleaner.merge_list_field(existing, incoming, 'securityLabel')
        BatchCleaner.merge_list_field(existing, incoming, 'tag')

        # keep highest rating/confidence
        for field in ('rating', 'confidence'):
            if field in incoming:
                existing[field] = max(existing.get(field, 0), incoming.get(field, 0))

        # keep earliest externalDateAdded and latest externalLastModified
        to_dt = DatetimeOperation.any_to_datetime
        date_merge_rules = (
            ('externalDateAdded', min),
            ('externalDateLastModified', max),
        )
        for field, resolve in date_merge_rules:
            if field in incoming:
                existing_val = existing.get(field, incoming[field])
                try:
                    existing[field] = resolve(existing_val, incoming[field], key=to_dt)
                except Exception:
                    _logger.exception(f'Invalid date specified for {field}')

        # combine attributes and later the cleaning pass will dedup/truncate
        incoming_attrs = incoming.get('attribute') or []
        if incoming_attrs:
            existing['attribute'] = (existing.get('attribute') or []) + incoming_attrs

        return existing

    @staticmethod
    def combine_file_hashes(existing_summary: str, new_summary: str) -> str:
        """Combine two File indicator summaries into a single multi-hash summary.

        Args:
            existing_summary: The summary from the already-collected indicator.
            new_summary: The summary from the incoming indicator.

        Returns:
            A combined summary with hashes in md5 : sha1 : sha256 order.
        """
        hash_type_by_len = {32: 'md5', 40: 'sha1', 64: 'sha256'}

        all_hashes = [h.strip() for h in new_summary.split(' : ')]
        all_hashes.extend(h.strip() for h in existing_summary.split(' : '))

        hash_values: dict[str, str] = {}
        for hash_value in all_hashes:
            hash_type = hash_type_by_len.get(len(hash_value))
            if hash_type:
                hash_values[hash_type] = hash_value

        return ' : '.join(hash_values[ht] for ht in ['md5', 'sha1', 'sha256'] if ht in hash_values)

    @staticmethod
    def _file_hash_set(summary: str) -> set[str]:
        """Extract individual hashes from a File indicator summary.

        Args:
            summary: A File indicator summary string (e.g. 'md5 : sha1 : sha256').

        Returns:
            A set of individual hash strings with whitespace stripped.
        """
        return {h.strip() for h in summary.split(' : ') if h.strip()}

    @cached_property
    def naics_tags(self) -> NAICSTags:
        """NAICS Tags"""
        return NAICSTags()

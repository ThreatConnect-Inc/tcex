"""TcEx Framework Module"""

from typing import Any
from unittest.mock import MagicMock, PropertyMock

import pytest

from tcex.api.tc.v2.batch.batch_submit import BatchSubmit


class TestBatchCleanContent:
    """Test the BatchSubmit clean_content feature."""

    @pytest.fixture
    def batch_submit(self) -> BatchSubmit:
        """Create a BatchSubmit instance with mocked dependencies."""
        mock_inputs = MagicMock()
        mock_session = MagicMock()
        batch = BatchSubmit(
            inputs=mock_inputs,
            session_tc=mock_session,
            owner='TestOwner',
        )
        return batch

    @pytest.fixture
    def sample_content(self) -> dict:
        """Return the sample content for testing.

        Note: The _clean_attributes method expects 'groups'/'indicators' (plural) and
        'attributes' (plural) keys, which differs from the raw batch API format.
        """
        return {
            'groups': [],
            'indicators': [
                {
                    'attributes': [
                        {'type': 'Events', 'value': 'A duplicate attribute.'},
                        {'type': 'Events', 'value': 'A duplicate attribute.'},
                        {
                            'type': 'Events',
                            'value': (
                                "The world awakens with dawn's first light, painting the sky in "
                                'shades of gold and crimson. Birdsong fills the surrounding air, '
                                'a beautiful symphony of joy and life eternal. Mountains stand '
                                'majestic and eternal, their peaks touching distant clouds above. '
                                'Forests breathe with ancient wisdom, harboring secrets of ages '
                                'long past. Rivers flow endlessly forward, carrying incredible '
                                'stories of distant lands. Every creature plays its vital role in '
                                "nature's grand and perfect design. The wind whispers gently "
                                'through valleys, carrying hope and boundless promise. Stars '
                                'emerge as darkness falls, like diamonds scattered across velvet '
                                'night sky. In this vast universe, we find our place.'
                            ),
                        },
                    ],
                    'rating': 3.0,
                    'summary': 'http://dqpo.my.id/',
                    'type': 'URL',
                }
            ],
        }

    @staticmethod
    def test_deduplication_removes_duplicate_attributes(
        batch_submit: BatchSubmit, sample_content: dict[Any, Any]
    ):
        """Test that duplicate attributes are removed."""
        # Mock attribute_config to return no max size (no truncation)
        type(batch_submit).attribute_config = PropertyMock(return_value={})

        result = batch_submit.clean_content(sample_content)

        # The two duplicate "A duplicate attribute." entries should be deduplicated to one
        indicator = result['indicators'][0]
        attributes = indicator['attributes']

        # Count occurrences of "A duplicate attribute."
        duplicate_count = sum(1 for attr in attributes if attr['value'] == 'A duplicate attribute.')
        assert duplicate_count == 1, 'Duplicate attributes should be removed'

        # We should have 2 unique attributes (1 deduplicated + 1 long one)
        assert len(attributes) == 2

    @staticmethod
    def test_auto_truncation_truncates_long_attributes(
        batch_submit: BatchSubmit, sample_content: dict[Any, Any]
    ):
        """Test that long attribute values are truncated based on maxSize."""
        # Mock attribute_config to return a maxSize for Events
        max_size = 100
        type(batch_submit).attribute_config = PropertyMock(
            return_value={'Events': {'maxSize': max_size}}
        )

        result = batch_submit.clean_content(sample_content)

        indicator = result['indicators'][0]
        attributes = indicator['attributes']

        # Find the long attribute (it should now be truncated)
        long_attr = next(
            (attr for attr in attributes if attr['value'].startswith('The world')), None
        )
        assert long_attr is not None, 'Long attribute should exist'
        assert len(long_attr['value']) == max_size, (
            f'Attribute should be truncated to {max_size} characters'
        )
        assert long_attr['value'].endswith('...'), 'Truncated attribute should end with ellipsis'

    @staticmethod
    def test_truncation_creates_new_duplicates_that_get_deduplicated(batch_submit: BatchSubmit):
        """Test that attributes that become duplicates after truncation are deduplicated."""
        # Create content with two different long values that will truncate to the same value
        content = {
            'groups': [],
            'indicators': [
                {
                    'attributes': [
                        {'type': 'Events', 'value': 'Short prefix - AAAAAAAAAA'},
                        {'type': 'Events', 'value': 'Short prefix - BBBBBBBBBB'},
                    ],
                    'rating': 3.0,
                    'summary': 'http://example.com/',
                    'type': 'URL',
                }
            ],
        }

        # Set maxSize to truncate both to "Short prefix..."
        max_size = 15
        type(batch_submit).attribute_config = PropertyMock(
            return_value={'Events': {'maxSize': max_size}}
        )

        result = batch_submit.clean_content(content)

        indicator = result['indicators'][0]
        attributes = indicator['attributes']

        # Both should truncate to "Short prefix..." and then be deduplicated to one
        assert len(attributes) == 1, 'Truncated duplicates should be deduplicated'
        assert attributes[0]['value'] == 'Short prefix...'

    @staticmethod
    def test_clean_content_handles_string_input(batch_submit: BatchSubmit):
        """Test that clean_content can handle JSON string input."""
        import json

        type(batch_submit).attribute_config = PropertyMock(return_value={})

        content = {
            'groups': [],
            'indicators': [
                {
                    'attributes': [
                        {'type': 'Events', 'value': 'Test attribute'},
                        {'type': 'Events', 'value': 'Test attribute'},
                    ],
                    'rating': 3.0,
                    'summary': 'http://example.com/',
                    'type': 'URL',
                }
            ],
        }

        # Pass as JSON string
        result = batch_submit.clean_content(json.dumps(content))

        indicator = result['indicators'][0]
        assert len(indicator['attributes']) == 1, 'Duplicates should be removed from string input'

    @staticmethod
    def test_clean_content_preserves_non_duplicate_attributes(batch_submit: BatchSubmit):
        """Test that non-duplicate attributes are preserved."""
        type(batch_submit).attribute_config = PropertyMock(return_value={})

        content = {
            'groups': [],
            'indicators': [
                {
                    'attributes': [
                        {'type': 'Events', 'value': 'First unique value'},
                        {'type': 'Events', 'value': 'Second unique value'},
                        {'type': 'Description', 'value': 'A description'},
                    ],
                    'rating': 3.0,
                    'summary': 'http://example.com/',
                    'type': 'URL',
                }
            ],
        }

        result = batch_submit.clean_content(content)

        indicator = result['indicators'][0]
        assert len(indicator['attributes']) == 3, 'All unique attributes should be preserved'

    @staticmethod
    def test_clean_content_skips_empty_values(batch_submit: BatchSubmit):
        """Test that attributes with empty or None values are skipped."""
        type(batch_submit).attribute_config = PropertyMock(return_value={})

        content = {
            'groups': [],
            'indicators': [
                {
                    'attributes': [
                        {'type': 'Events', 'value': 'Valid value'},
                        {'type': 'Events', 'value': ''},
                        {'type': 'Events', 'value': None},
                    ],
                    'rating': 3.0,
                    'summary': 'http://example.com/',
                    'type': 'URL',
                }
            ],
        }

        result = batch_submit.clean_content(content)

        indicator = result['indicators'][0]
        assert len(indicator['attributes']) == 1, 'Empty/None values should be skipped'
        assert indicator['attributes'][0]['value'] == 'Valid value'

    @staticmethod
    def test_clean_content_works_with_groups(batch_submit: BatchSubmit):
        """Test that clean_content also processes groups."""
        type(batch_submit).attribute_config = PropertyMock(return_value={})

        content = {
            'groups': [
                {
                    'name': 'Test Group',
                    'type': 'Adversary',
                    'attributes': [
                        {'type': 'Description', 'value': 'Duplicate description'},
                        {'type': 'Description', 'value': 'Duplicate description'},
                    ],
                }
            ],
            'indicators': [],
        }

        result = batch_submit.clean_content(content)

        group = result['groups'][0]
        assert len(group['attributes']) == 1, 'Group duplicate attributes should be deduplicated'

    @staticmethod
    def test_no_truncation_when_within_limit(batch_submit: BatchSubmit):
        """Test that values within the maxSize limit are not truncated."""
        max_size = 100
        type(batch_submit).attribute_config = PropertyMock(
            return_value={'Events': {'maxSize': max_size}}
        )

        short_value = 'This is a short value'
        content = {
            'groups': [],
            'indicators': [
                {
                    'attributes': [{'type': 'Events', 'value': short_value}],
                    'rating': 3.0,
                    'summary': 'http://example.com/',
                    'type': 'URL',
                }
            ],
        }

        result = batch_submit.clean_content(content)

        indicator = result['indicators'][0]
        assert indicator['attributes'][0]['value'] == short_value, (
            'Short values should not be modified'
        )

    @staticmethod
    def test_truncation_with_tiny_max_size(batch_submit: BatchSubmit):
        """Test truncation behavior when maxSize is smaller than ellipsis length."""
        max_size = 2  # Smaller than '...'
        type(batch_submit).attribute_config = PropertyMock(
            return_value={'Events': {'maxSize': max_size}}
        )

        content = {
            'groups': [],
            'indicators': [
                {
                    'attributes': [{'type': 'Events', 'value': 'Long value that needs truncation'}],
                    'rating': 3.0,
                    'summary': 'http://example.com/',
                    'type': 'URL',
                }
            ],
        }

        result = batch_submit.clean_content(content)

        indicator = result['indicators'][0]
        # When maxSize <= ellipsis length, it should do a hard cut without ellipsis
        assert len(indicator['attributes'][0]['value']) == max_size
        assert indicator['attributes'][0]['value'] == 'Lo'

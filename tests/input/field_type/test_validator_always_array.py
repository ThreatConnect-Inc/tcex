"""TcEx Framework Module"""

# standard library

# third-party
import pytest
from pydantic import BaseModel, Field

# first-party
from tcex.input.field_type import always_array
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest


class TestInputsFieldTypes(InputTest):
    """Test TcEx String Field Model Tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()

    @pytest.mark.parametrize(
        'value,include_empty,include_null,split_csv,strip,expected',
        [
            # Test single string with default behavior
            ('abc', False, False, False, False, ['abc']),

            # Test CSV split without strip
            ('a, b ,c ', False, False, True, False, ['a', ' b ', 'c ']),

            # Test CSV split with strip
            ('a, b ,c ', False, False, True, True, ['a', 'b', 'c']),

            # Test empty string with include_empty = True
            ('', True, False, False, False, ['']),

            # Test None with include_null = True
            (None, False, True, False, False, [None]),

            # Test existing list
            (['x', 'y'], False, False, False, False, ['x', 'y']),

            # Test stripping elements in list
            ([' x ', ' y '], False, False, False, True, ['x', 'y']),
        ],
    )
    def test_validator_always_array(
        self,
        value: str,
        include_empty: bool,
        include_null: bool,
        split_csv: bool,
        strip: bool,
        expected: bool,
    ):
        """Test the always_array validator."""

        class DummyModel(BaseModel):
            """Dummy model for testing."""
            name: str = Field(default='dummy')

        model = DummyModel()
        validator = always_array(
            allow_empty=include_empty,
            include_empty=include_empty,
            include_null=include_null,
            split_csv=split_csv,
            strip=strip,
        )
        assert validator(value, model) == expected # type: ignore

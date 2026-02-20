"""TcEx Framework Module"""

import pytest
from pydantic import BaseModel, Field

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
            pytest.param('abc', False, False, False, False, ['abc'], id='single-string'),
            pytest.param(
                'a, b ,c ', False, False, True, False, ['a', ' b ', 'c '], id='csv-split-no-strip'
            ),
            pytest.param(
                'a, b ,c ', False, False, True, True, ['a', 'b', 'c'], id='csv-split-with-strip'
            ),
            pytest.param('', True, False, False, False, [''], id='include-empty-string'),
            pytest.param(None, False, True, False, False, [None], id='include-null-value'),
            pytest.param(['x', 'y'], False, False, False, False, ['x', 'y'], id='existing-list'),
            pytest.param(
                [' x ', ' y '], False, False, False, True, ['x', 'y'], id='strip-elements-in-list'
            ),
        ],
    )
    def test_validator_always_array(
        self,
        value: str,
        include_empty: bool,
        include_null: bool,
        split_csv: bool,
        strip: bool,
        expected: list,
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
        assert validator(value, model) == expected  # type: ignore

"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils import Utils


class TestUtilsRemoveNone:
    """Test Suite"""

    utils = Utils()

    @pytest.mark.parametrize(
        'dict_,expected',
        [
            ({}, {}),
            ({'none': None}, {}),
            ({'one': 1, 'two': 2, 'three': None}, {'one': 1, 'two': 2}),
        ],
    )
    def test_utils_remove_none(self, dict_: dict, expected: dict):
        """Test Case"""
        flattened_list = self.utils.remove_none(dict_)
        assert flattened_list == expected

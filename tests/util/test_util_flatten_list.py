"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.util import Util


class TestUtilFlattenList:
    """Test Suite"""

    util = Util()

    @pytest.mark.parametrize(
        'lst,expected',
        [
            ([1, 2, 3], [1, 2, 3]),
            ([[1, 2, 3], [4, 5, 6]], [1, 2, 3, 4, 5, 6]),
            ([[1, 2, 3], [4, 5, [6, 7]]], [1, 2, 3, 4, 5, 6, 7]),
            ([[1, 2, 3], [4, 5, 6], 7], [1, 2, 3, 4, 5, 6, 7]),
        ],
    )
    def test_utils_flatten_list(self, lst: list, expected: list):
        """Test Case"""
        flattened_list = self.util.flatten_list(lst)
        assert flattened_list == expected

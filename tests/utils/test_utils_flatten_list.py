"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils import Utils


class TestUtilsFlattenList:
    """Test Suite"""

    utils = Utils()

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
        flattened_list = self.utils.flatten_list(lst)
        assert flattened_list == expected

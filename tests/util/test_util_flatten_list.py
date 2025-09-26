"""TestUtilFlattenList for testing list flattening functionality.

Test suite for validating the Util.flatten_list method functionality which converts
nested lists into a single flattened list structure.

Classes:
    TestUtilFlattenList: Test suite for list flattening operations

TcEx Module Tested: tcex.util.Util
"""


import pytest


from tcex.util import Util


class TestUtilFlattenList:
    """TestUtilFlattenList for testing list flattening functionality.

    Test suite for validating the Util.flatten_list method which converts nested lists
    into a single flattened list structure. Tests various nesting scenarios including
    simple lists, multi-level nested lists, and mixed element types.
    """

    util = Util()

    @pytest.mark.parametrize(
        'lst,expected',
        [
            pytest.param([1, 2, 3], [1, 2, 3], id='pass-already-flat-list'),
            pytest.param([[1, 2, 3], [4, 5, 6]], [1, 2, 3, 4, 5, 6], id='pass-simple-nested-lists'),
            pytest.param(
                [[1, 2, 3], [4, 5, [6, 7]]], [1, 2, 3, 4, 5, 6, 7], id='pass-multi-level-nested'
            ),
            pytest.param(
                [[1, 2, 3], [4, 5, 6], 7], [1, 2, 3, 4, 5, 6, 7], id='pass-mixed-nested-and-element'
            ),
        ],
    )
    def test_utils_flatten_list(self, lst: list, expected: list):
        """Test Case for list flattening functionality.

        Test that validates the Util.flatten_list method correctly flattens nested lists
        into a single-level list structure. Tests various scenarios including simple lists,
        multi-level nested lists, and mixed element types to ensure proper flattening behavior.
        """
        flattened_list = self.util.flatten_list(lst)
        assert flattened_list == expected

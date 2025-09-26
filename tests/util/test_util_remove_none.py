"""TestUtilRemoveNone for utility remove_none functionality.

Test suite for the Util.remove_none method that removes None values from dictionaries.

Classes:
    TestUtilRemoveNone: Test suite for remove_none utility method

TcEx Module Tested: tcex.util
"""


import pytest


from tcex.util import Util


class TestUtilRemoveNone:
    """TestUtilRemoveNone for utility remove_none functionality.

    Test suite for the Util.remove_none method that removes None values from
    dictionaries.
    """

    @pytest.mark.parametrize(
        'dict_,expected',
        [
            pytest.param({}, {}, id='pass-empty-dict'),
            pytest.param({'none': None}, {}, id='pass-dict-with-none'),
            pytest.param(
                {'one': 1, 'two': 2, 'three': None},
                {'one': 1, 'two': 2},
                id='pass-dict-with-mixed-values',
            ),
        ],
    )
    def test_utils_remove_none(self, dict_: dict, expected: dict):
        """Test remove_none utility method functionality.

        Test case for the Util.remove_none method that removes None values from
        dictionaries while preserving other values.
        """
        flattened_list = Util.remove_none(dict_)
        assert flattened_list == expected

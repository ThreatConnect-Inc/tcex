"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.util.string_operation import StringOperation


class TestStringOperationRandomString:
    """Test Suite"""

    so = StringOperation()

    @pytest.mark.parametrize(
        'string_length',
        [(0), (1), (55), (100), (1000)],
    )
    def test_string_operation_random_string(self, string_length):
        """Test Case"""
        result = self.so.random_string(string_length=string_length)
        assert (
            len(result) == string_length
        ), f'The length of the string {len(result)} != {string_length}'

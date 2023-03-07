"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils.string_operations import StringOperations


class TestStringOperationsRandomString:
    """Test Suite"""

    so = StringOperations()

    @pytest.mark.parametrize(
        'string_length',
        [(0), (1), (55), (100), (1000)],
    )
    def test_string_operations_random_string(self, string_length):
        """Test Case"""
        result = self.so.random_string(string_length=string_length)
        assert (
            len(result) == string_length
        ), f'The length of the string {len(result)} != {string_length}'

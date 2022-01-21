"""Test the TcEx Utils Module."""
# first-party
from tcex.utils import Utils


class TestFlattenList:
    """Test the TcEx Utils Module."""

    @staticmethod
    def test_flat_list():
        """Test Case"""
        lst = [1, 2, 3]
        flattened_list = Utils().flatten_list(lst)
        assert flattened_list == lst

    @staticmethod
    def test_list_of_lists():
        """Test Case"""
        lst = [[1, 2, 3], [4, 5, 6]]
        flattened_list = Utils().flatten_list(lst)
        assert flattened_list == [1, 2, 3, 4, 5, 6]

    @staticmethod
    def test_list_of_lists_depth():
        """Test Case"""
        lst = [[1, 2, 3], [4, 5, [6, 7]]]
        flattened_list = Utils().flatten_list(lst)
        assert flattened_list == [1, 2, 3, 4, 5, 6, 7]

    @staticmethod
    def test_list_of_lists_and_singles():
        """Test Case"""
        lst = [[1, 2, 3], [4, 5, 6], 7]
        flattened_list = Utils().flatten_list(lst)
        assert flattened_list == [1, 2, 3, 4, 5, 6, 7]

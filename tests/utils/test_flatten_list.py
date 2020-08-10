"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class TestFlattenList:
    """Test the TcEx Utils Module."""

    def test_flat_list(self, tcex):
        """Test a list that's already flat

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        lst = [1, 2, 3]
        flst = tcex.utils.flatten_list(lst)
        assert flst == lst

    def test_list_of_lists(self, tcex):
        """Test a list that's comprised of other lists

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        lst = [[1, 2, 3], [4, 5, 6]]
        flst = tcex.utils.flatten_list(lst)
        assert flst == [1, 2, 3, 4, 5, 6]

    def test_list_of_lists_depth(self, tcex):
        """Test a list that's comprised of other lists that have other lists (arbitrary depth)

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        lst = [[1, 2, 3], [4, 5, [6, 7]]]
        flst = tcex.utils.flatten_list(lst)
        assert flst == [1, 2, 3, 4, 5, 6, 7]

    def test_list_of_lists_and_singles(self, tcex):
        """Test a list that's comprised of other lists and single values

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        lst = [[1, 2, 3], [4, 5, 6], 7]
        flst = tcex.utils.flatten_list(lst)
        assert flst == [1, 2, 3, 4, 5, 6, 7]

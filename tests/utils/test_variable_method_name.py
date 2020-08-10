"""Test the TcEx Utils Module."""


# pylint: disable=no-self-use
class TestVariableMethodName:
    """Test the TcEx Utils Module."""

    def test_variable_to_method(self, tcex):
        """Test an converting playbook variable to method

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        method = tcex.utils.variable_method_name('#App:9876:string.operation!String')
        assert method == 'string_operation_string'

"""TestStringOperationToBool for testing StringOperation boolean conversion functionality.

This module contains test cases for the StringOperation class, specifically testing
the to_bool method that converts various input types to boolean values.

Classes:
    TestStringOperationToBool: Test suite for StringOperation boolean conversion methods

TcEx Module Tested: tcex.util.string_operation
"""


import pytest


from tcex.util.string_operation import StringOperation


class TestStringOperationToBool:
    """TestStringOperationToBool for testing StringOperation boolean conversion functionality.

    This test class provides comprehensive testing for the StringOperation class
    to_bool method that handles conversion of various input types to boolean values.
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'string,expected',
        [
            pytest.param('true', True, id='pass-string-true-to-bool'),
            pytest.param('1', True, id='pass-string-one-to-bool'),
            pytest.param(1, True, id='pass-int-one-to-bool'),
            pytest.param(True, True, id='pass-bool-true-to-bool'),
            pytest.param('false', False, id='pass-string-false-to-bool'),
            pytest.param('0', False, id='pass-string-zero-to-bool'),
            pytest.param(0, False, id='pass-int-zero-to-bool'),
            pytest.param(False, False, id='pass-bool-false-to-bool'),
        ],
    )
    def test_string_operation_to_bool(self, string: str, expected: str) -> None:
        """Test boolean conversion functionality for various input types.

        This test case verifies that the to_bool method correctly converts
        various input types including strings, integers, and booleans to
        their corresponding boolean representations.

        Parameters:
            string: Input value to convert to boolean
            expected: Expected boolean conversion result
        """
        result = self.so.to_bool(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

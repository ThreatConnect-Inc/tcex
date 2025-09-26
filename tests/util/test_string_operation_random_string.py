"""TestStringOperationRandomString for string operation random string functionality.

Test suite for the StringOperation utility class that handles random string
generation with specified lengths for testing and development purposes.

Classes:
    TestStringOperationRandomString: Test suite for string operation random string methods

TcEx Module Tested: tcex.util.string_operation
"""


import pytest


from tcex.util.string_operation import StringOperation


class TestStringOperationRandomString:
    """TestStringOperationRandomString for string operation random string functionality.

    Test suite for the StringOperation utility class that handles random string
    generation with specified lengths for testing and development purposes.

    Attributes:
        so: Instance of StringOperation class for testing
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'string_length',
        [
            pytest.param(0, id='pass-zero-length'),
            pytest.param(1, id='pass-single-character'),
            pytest.param(55, id='pass-medium-length'),
            pytest.param(100, id='pass-long-length'),
            pytest.param(1000, id='pass-very-long-length'),
        ],
    )
    def test_string_operation_random_string(self, string_length):
        """Test random string generation functionality.

        Test case for the random_string method that generates random strings
        of specified lengths and verifies the output length matches the input
        parameter.
        """
        result = self.so.random_string(string_length=string_length)
        assert len(result) == string_length, (
            f'The length of the string {len(result)} != {string_length}'
        )

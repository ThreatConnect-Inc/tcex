"""TestStringOperationCamelCase for string operation camel case functionality.

Test suite for the StringOperation utility class that handles various string
transformations including camel case, pascal case, snake case, and space case
conversions.

Classes:
    TestStringOperationCamelCase: Test suite for string operation camel case methods

TcEx Module Tested: tcex.util.string_operation
"""


import pytest


from tcex.util.string_operation import StringOperation


class TestStringOperationCamelCase:
    """TestStringOperationCamelCase for string operation camel case functionality.

    Test suite for the StringOperation utility class that handles various string
    transformations including camel case, pascal case, snake case, and space case
    conversions.

    Attributes:
        so: Instance of StringOperation class for testing
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'string,pascal_case,plural,singular,snake_case,space_case',
        [
            pytest.param(
                'upperUpper',
                'UpperUpper',
                'upperUppers',
                'upperUpper',
                'upper_upper',
                'upper upper',
                id='pass-upper-upper-case',
            ),
            pytest.param(
                'testTEST',
                'TestTest',
                'testTESTs',
                'testTEST',
                'test_test',
                'test test',
                id='pass-test-test-case',
            ),
        ],
    )
    def test_string_operation_camel_string(
        self,
        string: str,
        pascal_case: str,
        plural: str,
        singular: str,
        snake_case: str,
        space_case: str,
    ):
        """Test camel string operation with multiple case conversions.

        Test case for the camel_string method that converts input strings to
        various case formats including pascal case, plural, singular, snake case,
        and space case.
        """
        camel_string = self.so.camel_string(string)
        assert camel_string.pascal_case() == pascal_case
        assert camel_string.plural() == plural
        assert camel_string.singular() == singular
        assert camel_string.snake_case() == snake_case
        assert camel_string.space_case() == space_case

    @pytest.mark.parametrize(
        'string,expected',
        [
            pytest.param('UpperUpper', 'upper_upper', id='pass-upper-upper'),
            pytest.param('lowerUpper', 'lower_upper', id='pass-lower-upper'),
            pytest.param('lowerlower', 'lowerlower', id='pass-lower-lower'),
            pytest.param('Upper', 'upper', id='pass-single-upper'),
        ],
    )
    def test_string_operation_camel_to_snake(self, string: str, expected: str):
        """Test camel case to snake case conversion.

        Test case for the camel_to_snake method that converts camel case strings
        to snake case format.
        """
        result = self.so.camel_to_snake(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'string,expected',
        [
            pytest.param('UpperUpper', 'upper upper', id='pass-upper-upper'),
            pytest.param('lowerUpper', 'lower upper', id='pass-lower-upper'),
            pytest.param('lowerlower', 'lowerlower', id='pass-lower-lower'),
            pytest.param('Upper', 'upper', id='pass-single-upper'),
        ],
    )
    def test_string_operation_camel_to_space(self, string: str, expected: str):
        """Test camel case to space case conversion.

        Test case for the camel_to_space method that converts camel case strings
        to space-separated format.

        Parameters:
            string: Input camel case string for conversion
            expected: Expected space case result
        """
        result = self.so.camel_to_space(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

"""TestStringOperationSnakeCase for testing StringOperation snake case functionality.

This module contains test cases for the StringOperation class, specifically testing
snake case string conversion methods including camel case, pascal case, plural,
singular, and space case transformations.

Classes:
    TestStringOperationSnakeCase: Test suite for StringOperation snake case methods

TcEx Module Tested: tcex.util.string_operation
"""


import pytest


from tcex.util.string_operation import StringOperation


class TestStringOperationSnakeCase:
    """TestStringOperationSnakeCase for testing StringOperation snake case functionality.

    This test class provides comprehensive testing for the StringOperation class
    methods that handle snake case string transformations and conversions.
    """

    so = StringOperation()

    @pytest.mark.parametrize(
        'string,camel_case,pascal_case,plural,singular,space_case',
        [
            pytest.param(
                'upper_upper',
                'upperUpper',
                'UpperUpper',
                'upper_uppers',
                'upper_upper',
                'Upper Upper',
                id='pass-snake-case-conversion',
            ),
        ],
    )
    def test_string_operation_snake_string(
        self,
        string: str,
        camel_case: str,
        pascal_case: str,
        plural: str,
        singular: str,
        space_case: str,
    ) -> None:
        """Test snake string conversion for comprehensive string transformations.

        This test case verifies that the snake_string method correctly converts
        snake case strings to various formats including camel case, pascal case,
        plural, singular, and space case representations.

        Parameters:
            string: Input snake case string to test
            camel_case: Expected camel case conversion result
            pascal_case: Expected pascal case conversion result
            plural: Expected plural form result
            singular: Expected singular form result
            space_case: Expected space case conversion result
        """
        snake_string = self.so.snake_string(string)
        assert snake_string.camel_case() == camel_case
        assert snake_string.pascal_case() == pascal_case
        assert snake_string.plural() == plural
        assert snake_string.singular() == singular
        assert snake_string.space_case() == space_case

    @pytest.mark.parametrize(
        'string,expected',
        [
            pytest.param('upper_upper', 'UpperUpper', id='pass-upper-upper-to-pascal'),
            pytest.param('lower_upper', 'LowerUpper', id='pass-lower-upper-to-pascal'),
            pytest.param('lowerlower', 'Lowerlower', id='pass-lowerlower-to-pascal'),
            pytest.param('upper', 'Upper', id='pass-upper-to-pascal'),
        ],
    )
    def test_string_operation_snake_to_pascal(self, string: str, expected: str) -> None:
        """Test snake to pascal case conversion functionality.

        This test case verifies that the snake_to_pascal method correctly converts
        snake case strings to pascal case format with proper capitalization.

        Parameters:
            string: Input snake case string to convert
            expected: Expected pascal case conversion result
        """
        result = self.so.snake_to_pascal(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'string,expected',
        [
            pytest.param('upper_upper', 'upperUpper', id='pass-upper-upper-to-camel'),
            pytest.param('lower_upper', 'lowerUpper', id='pass-lower-upper-to-camel'),
            pytest.param('lowerlower', 'lowerlower', id='pass-lowerlower-to-camel'),
            pytest.param('upper', 'upper', id='pass-upper-to-camel'),
        ],
    )
    def test_string_operation_snake_to_camel(self, string: str, expected: str) -> None:
        """Test snake to camel case conversion functionality.

        This test case verifies that the snake_to_camel method correctly converts
        snake case strings to camel case format with proper capitalization.

        Parameters:
            string: Input snake case string to convert
            expected: Expected camel case conversion result
        """
        result = self.so.snake_to_camel(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

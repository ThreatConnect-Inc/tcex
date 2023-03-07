"""Test Suite"""
# third-party
import pytest

# first-party
from tcex.utils.string_operations import StringOperations


class TestStringOperationsCamelCase:
    """Test Suite"""

    so = StringOperations()

    @pytest.mark.parametrize(
        'string,pascal_case,plural,singular,snake_case,space_case',
        [
            ('upperUpper', 'UpperUpper', 'upperUppers', 'upperUpper', 'upper_upper', 'upper upper'),
        ],
    )
    def test_string_operations_camel_string(
        self,
        string: str,
        pascal_case: str,
        plural: str,
        singular: str,
        snake_case: str,
        space_case: str,
    ):
        """Test Case"""
        camel_string = self.so.camel_string(string)
        assert camel_string.pascal_case() == pascal_case
        assert camel_string.plural() == plural
        assert camel_string.singular() == singular
        assert camel_string.snake_case() == snake_case
        assert camel_string.space_case() == space_case

    @pytest.mark.parametrize(
        'string,expected',
        [
            ('UpperUpper', 'upper_upper'),
            ('lowerUpper', 'lower_upper'),
            ('lowerlower', 'lowerlower'),
            ('Upper', 'upper'),
        ],
    )
    def test_string_operations_camel_to_snake(self, string: str, expected: str):
        """Test Case"""
        result = self.so.camel_to_snake(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'string,expected',
        [
            ('UpperUpper', 'upper upper'),
            ('lowerUpper', 'lower upper'),
            ('lowerlower', 'lowerlower'),
            ('Upper', 'upper'),
        ],
    )
    def test_string_operations_camel_to_space(self, string: str, expected: str):
        """Test Case"""
        result = self.so.camel_to_space(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

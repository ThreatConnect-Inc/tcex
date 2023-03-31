"""TcEx Framework Module"""
# third-party
import pytest

# first-party
from tcex.util.string_operation import StringOperation


class TestStringOperationSnakeCase:
    """Test Suite"""

    so = StringOperation()

    @pytest.mark.parametrize(
        'string,camel_case,pascal_case,plural,singular,space_case',
        [
            (
                'upper_upper',
                'upperUpper',
                'UpperUpper',
                'upper_uppers',
                'upper_upper',
                'Upper Upper',
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
    ):
        """Test Case"""
        snake_string = self.so.snake_string(string)
        assert snake_string.camel_case() == camel_case
        assert snake_string.pascal_case() == pascal_case
        assert snake_string.plural() == plural
        assert snake_string.singular() == singular
        assert snake_string.space_case() == space_case

    @pytest.mark.parametrize(
        'string,expected',
        [
            ('upper_upper', 'UpperUpper'),
            ('lower_upper', 'LowerUpper'),
            ('lowerlower', 'Lowerlower'),
            ('upper', 'Upper'),
        ],
    )
    def test_string_operation_snake_to_pascal(self, string: str, expected: str):
        """Test Case"""
        result = self.so.snake_to_pascal(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

    @pytest.mark.parametrize(
        'string,expected',
        [
            ('upper_upper', 'upperUpper'),
            ('lower_upper', 'lowerUpper'),
            ('lowerlower', 'lowerlower'),
            ('upper', 'upper'),
        ],
    )
    def test_string_operation_snake_to_camel(self, string: str, expected: str):
        """Test Case"""
        result = self.so.snake_to_camel(string)
        assert result == expected, f'Input {string} result of {result} != {expected}'

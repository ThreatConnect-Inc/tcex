"""Test the not_in validator."""
# first-party
from tcex.validators import ValidationError, not_in


class TestNotIn:
    """Test the not_in validator."""

    @staticmethod
    def tests_multi_values():
        """Test handling of multiple invalid values."""
        validator = not_in(['foo', None])

        try:
            validator('foo', 'test_arg', 'Test Arg')
            assert False, 'not_in validator should have failed!'
        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) cannot be in ["foo", None]'
            ), 'not_in validator raised exception with incorrect message.'

    @staticmethod
    def test_happy_path():
        """Test passing arg value."""
        validator = not_in(['foo'])

        try:
            validator('bar', 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'not_in should not have thrown exception.'

    @staticmethod
    def tests_string_array():
        """Test string array."""
        validator = not_in([[], ''])

        try:
            validator([], 'test_arg', 'Test Arg')
            assert False, 'Validator should have failed!'
        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) cannot be in [[], ""]'
            ), 'not_in validator raised exception with incorrect message.'

    @staticmethod
    def tests_string_array_happy():
        """Test a passing string array."""
        validator = not_in([[]])

        try:
            validator(['foo'], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'not_in should not have thrown exception.'

"""Test the in_range validator."""
# first-party
from tcex.validators import ValidationError, in_range


class TestInRange:
    """Test the in_range validator."""

    @staticmethod
    def test_happy_path_string():
        """Happy path test with a string"""
        validator = in_range(0, 100)

        try:
            validator(10, 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'in_range threw exception when it should have passed'

    @staticmethod
    def test_happy_path_string_array():
        """Happy path test with a string array"""
        validator = in_range(0, 100)

        try:
            validator([10, 15, 20], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'in_range threw exception when it should have passed'

    @staticmethod
    def test_boundaries():
        """Test values on the min and max boundaries"""
        validator = in_range(0, 100)

        try:
            validator([0, 100], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'in_range threw exception when it should have passed'

    @staticmethod
    def test_fail_lower_string():
        """Test failure because of lower bound."""
        validator = in_range(0, 100)

        try:
            validator(-1, 'test_arg', 'Test Arg')
            assert False, 'Validator should have failed!'

        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) is not between 0 and 100.'
            ), 'Validator failed with incorrect message'

    @staticmethod
    def test_fail_upper_string():
        """Test failure because of upper bound."""
        validator = in_range(0, 100)

        try:
            validator(101, 'test_arg', 'Test Arg')
            assert False, 'Validator should have failed!'

        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) is not between 0 and 100.'
            ), 'Validator failed with incorrect message'

    @staticmethod
    def test_fail_string_array():
        """Test failure in an array."""
        validator = in_range(0, 100)

        try:
            validator([101, 100], 'test_arg', 'Test Arg')
            assert False, 'Validator should have failed!'
        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) is not between 0 and 100.'
            ), 'Validator failed with incorrect message'

    @staticmethod
    def test_allow_none_true():
        """Test allow_none."""
        validator = in_range(0, 100, allow_none=True)

        try:
            validator([None, 100], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'in_range threw exception when it should have passed'

"""Test transforms."""
# standard library
from functools import reduce

# first-party
from tcex.validators import ValidationError, to_bool, to_float, to_int


class TestIsType:
    """Test transforms."""

    # to_int tests
    @staticmethod
    def test_to_int():
        """Test to_int transform."""
        validator = to_int()

        try:
            assert validator('10', 'test_arg', 'Test Arg') == 10
        except ValidationError:
            assert False, '"Test Arg" (to_int) failed when it should have passed.'

    @staticmethod
    def test_to_int_none():
        """Test to_int transform with none."""
        validator = to_int(allow_none=True)

        try:
            assert validator(None, 'test_arg', 'Test Arg') is None
        except ValidationError:
            assert False, '"Test Arg" (to_int) failed when it should have passed.'

    @staticmethod
    def test_to_int_negative():
        """Test to_int transform that should fail."""
        validator = to_int()

        try:
            validator('foo', 'test_arg', 'Test Arg')
            assert False, 'Validator passed when it should have failed.'
        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) must be a int.'
            ), 'Validator failed with an incorrect message.'

    @staticmethod
    def test_to_int_array():
        """Test to_int transform with an array."""
        validator = to_int()

        try:
            validator(['10', '11', '-12'], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, '"Test Arg" (to_int) failed when it should have passed.'

    @staticmethod
    def test_to_int_array_none_ok():
        """Test to_int transform with arrays and Nones."""
        validator = to_int(allow_none=True)

        try:
            validator(['10', '11', None, '-12'], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, '"Test Arg" (to_int) failed when it should have passed.'

    @staticmethod
    def test_to_int_array_not_none_ok():
        """Test to_int transform with None in arrays that should fail."""
        validator = to_int()

        try:
            validator(['10', '11', None, '-12'], 'test_arg', 'Test Arg')
            assert False, 'Validator passed when it should have failed.'
        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) must be a int.'
            ), 'Validator failed with an incorrect message.'

    @staticmethod
    def test_is_float():
        """Test to_float transform."""
        validator = to_float()

        try:
            validator('10.5', 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, '"Test Arg" (is_float) failed when it should have passed.'

    @staticmethod
    def test_is_float_negative():
        """Test to_float transform that should fail."""
        validator = to_float()

        try:
            validator('foo', 'test_arg', 'Test Arg')
            assert False, 'Validator passed when it should have failed.'
        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) must be a float.'
            ), 'Validator failed with an incorrect message.'

    @staticmethod
    def test_is_float_array():
        """Test to_float transform with an array."""
        validator = to_float()

        try:
            validator(['10.5', '11', '-12.2'], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, '"Test Arg" (is_float) failed when it should have passed.'

    @staticmethod
    def test_is_float_array_none_ok():
        """Test to_float transform with an array and nones."""
        validator = to_float(allow_none=True)

        try:
            validator(['10.2', '11.3', None, '-12.5'], 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, '"Test Arg" (is_float) failed when it should have passed.'

    @staticmethod
    def test_is_float_array_not_none_ok():
        """Test to_float transform with an array and nones that should fail."""
        validator = to_float()

        try:
            validator(['10.2', '11.3', None, '-12.5'], 'test_arg', 'Test Arg')
            assert False, 'Validator passed when it should have failed.'
        except ValidationError as v:
            assert (
                v.message == '"Test Arg" (test_arg) must be a float.'
            ), 'Validator failed with an incorrect message.'

    @staticmethod
    def test_to_bool():
        """Test to_bool transform."""
        validator = to_bool()

        try:
            assert validator('true', 'test_arg', 'Test Arg')
        except ValidationError:
            assert False

    @staticmethod
    def test_to_bool_false():
        """Test to_bool transform with a false value."""
        validator = to_bool()

        try:
            assert not validator('false', 'test_arg', 'Test Arg')
        except ValidationError:
            assert False

    @staticmethod
    def test_to_bool_array():
        """Test to_bool transform with an array value."""
        validator = to_bool()

        try:
            assert reduce(lambda a, b: a and b, validator([1, 'true', 't'], 'test_arg', 'Test Arg'))
        except ValidationError:
            assert False

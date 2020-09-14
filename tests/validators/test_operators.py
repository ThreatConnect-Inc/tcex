"""Test the operator validators."""
# first-party
from tcex.validators import (
    ValidationError,
    equal_to,
    greater_than,
    greater_than_or_equal,
    less_than,
    less_than_or_equal,
)


class TestOperators:
    """Test the operator validators."""

    # equal_to
    @staticmethod
    def test_equal_to_happy():
        """Test the equal_to validator."""
        validator = equal_to('foo')

        try:
            validator('foo', 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'equal_to failed when it should have passed.'

    @staticmethod
    def test_equal_to_allow_none():
        """Test the equal_to validator with allow_none."""
        validator = equal_to('foo', allow_none=True)

        try:
            validator(None, 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'equal_to failed when it should have passed.'

    @staticmethod
    def test_equal_to_fail():
        """Test the equal_to validator when it should fail."""
        validator = equal_to('bar')

        try:
            validator('foo', 'test_arg', 'Test Arg')
            assert False, 'equal_to passed when it should have failed.'
        except ValidationError as v:
            assert v.message == '"Test Arg" (test_arg) is not equal to "bar"'

    # less_than
    @staticmethod
    def test_less_than_happy():
        """Test the less_than validator."""
        validator = less_than(12)

        try:
            validator(10, 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, '"Test Arg" (less_than failed when it should have passed.'

    @staticmethod
    def test_less_than_fail():
        """Test the less_than validator when it should fail."""
        validator = less_than(12)

        try:
            validator(12, 'test_arg', 'Test Arg')
            assert False, 'less_than passed when it should have failed.'
        except ValidationError as v:
            assert v.message == '"Test Arg" (test_arg) is not less than 12'

    # less_than_or_equal
    @staticmethod
    def test_less_than_or_equal_happy():
        """Test the less_than_or_equal validator."""
        validator = less_than_or_equal(12)

        try:
            validator(12, 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'less_than_or_equal failed when it should have passed.'

    @staticmethod
    def test_less_than_or_equal_fail():
        """Test the less_than_or_equal validator when it should fail."""
        validator = less_than_or_equal(12)

        try:
            validator(13, 'test_arg', 'Test Arg')
            assert False, 'less_than_or_equal passed when it should have failed.'
        except ValidationError as v:
            assert v.message == '"Test Arg" (test_arg) is not less than or equal to 12'

    # greater_than
    @staticmethod
    def test_greater_than_happy():
        """Test the greater_than validator."""
        validator = greater_than(12)

        try:
            validator(13, 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'greater_than failed when it should have passed.'

    @staticmethod
    def test_greater_than_fail():
        """Test the greater_than validator when it should fail."""
        validator = greater_than(12)

        try:
            validator(11, 'test_arg', 'Test Arg')
            assert False, 'greater_than passed when it should have failed.'
        except ValidationError as v:
            assert v.message == '"Test Arg" (test_arg) is not greater than 12'

    # greater_than_or_equal
    @staticmethod
    def test_greater_than_or_equal_happy():
        """Test the greater_than_or_equal validator."""
        validator = greater_than_or_equal(12)

        try:
            validator(12, 'test_arg', 'Test Arg')
        except ValidationError:
            assert False, 'greater_than_or_equal failed when it should have passed.'

    @staticmethod
    def test_greater_than_or_equal_fail():
        """Test the greater_than_or_equal validator when it should fail."""
        validator = greater_than_or_equal(12)

        try:
            validator(10, 'test_arg', 'Test Arg')
            assert False, 'greater_than_or_equal passed when it should have failed.'
        except ValidationError as v:
            assert v.message == '"Test Arg" (test_arg) is not greater than or equal to 12'

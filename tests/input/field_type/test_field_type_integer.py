"""TestInputsFieldTypes for Integer Field Type Testing.

This module provides comprehensive test cases for the Integer field type in TcEx Apps,
validating various input scenarios including basic functionality, optional fields,
constraint validation, array inputs, and union type handling with always_array validator.

Classes:
    TestInputsFieldTypes: Test suite for Integer field type validation

TcEx Module Tested: tcex.input.field_type.integer
"""


from collections.abc import Callable


import pytest
from pydantic import BaseModel, field_validator


from tcex.input.field_type import Integer, always_array, integer
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypes(InputTest):
    """TestInputsFieldTypes for Integer Field Type Validation.

    This test class provides comprehensive validation of the Integer field type functionality
    in TcEx Apps, including testing basic integer processing, constraint validation,
    array handling, union types, and optional field scenarios.

    Fixtures:
        playbook_app: MockApp fixture for creating test applications with integer field
            configurations
    """

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method resets scoped properties to ensure clean test isolation.
        """
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, int input
            pytest.param(1234, 1234, False, False, id='pass-required-int-input'),
            # required, string input
            pytest.param('1234', 1234, False, False, id='pass-required-string-input'),
            # optional, null input
            pytest.param(None, None, True, False, id='pass-optional-null-input'),
            #
            # Fail Testing
            #
            # required, empty input
            pytest.param('abc', '', False, True, id='fail-required-invalid-string'),
            # required, empty input
            pytest.param('', '', False, True, id='fail-required-empty-string'),
            # optional, empty input
            pytest.param('', '', True, True, id='fail-optional-empty-string'),
            # required, null input
            pytest.param(None, None, False, True, id='fail-required-null-input'),
        ],
    )
    def test_field_model_integer_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Integer field type with various input scenarios.

        This test validates basic Integer field type functionality including string to int
        conversion, optional field handling, and validation error scenarios.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications

        Args:
            input_value: The input value to test
            expected: The expected output value after processing
            optional: Whether the field is optional or required
            fail_test: Whether the test should expect a failure
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: Integer

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: Integer | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        ('input_value,expected,ge,gt,le,lt,optional,fail_test'),
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param(
                1234, 1234, None, None, None, None, False, False, id='pass-required-normal-input'
            ),
            # optional, null input
            pytest.param(
                None, None, None, None, None, None, True, False, id='pass-optional-null-input'
            ),
            # required, normal input, ge=1000
            pytest.param(
                1234, 1234, 1000, None, None, None, False, False, id='pass-required-ge-constraint'
            ),
            # required, normal input, gt=1000
            pytest.param(
                1234, 1234, None, 1000, None, None, False, False, id='pass-required-gt-constraint'
            ),
            # required, normal input, le=2000
            pytest.param(
                1234, 1234, None, None, 2000, None, False, False, id='pass-required-le-constraint'
            ),
            # required, normal input, lt=2000
            pytest.param(
                1234, 1234, None, None, None, 2000, False, False, id='pass-required-lt-constraint'
            ),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(
                None, None, True, None, None, None, False, True, id='fail-required-null-input'
            ),
            # required, empty input
            pytest.param(
                '', None, False, None, None, None, False, True, id='fail-required-empty-input'
            ),
            # required, normal input, ge=2000
            pytest.param(
                1234, 1234, 2000, None, None, None, False, True, id='fail-required-ge-violation'
            ),
            # required, normal input, gt=2000
            pytest.param(
                1234, 1234, None, 2000, None, None, False, True, id='fail-required-gt-violation'
            ),
            # required, normal input, le=1000
            pytest.param(
                1234, 1234, None, None, 1000, None, False, True, id='fail-required-le-violation'
            ),
            # required, normal input, lt=1000
            pytest.param(
                1234, 1234, None, None, None, 1000, False, True, id='fail-required-lt-violation'
            ),
        ],
    )
    def test_field_model_integer_custom_input(
        self,
        input_value: str,
        expected: str,
        ge: int,
        gt: int,
        le: int,
        lt: int,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Integer field type with custom constraints.

        This test validates custom Integer field type functionality with various constraint
        options including greater than, less than, greater than or equal, and less than or equal.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications

        Args:
            input_value: The input value to test
            expected: The expected output value after processing
            ge: Greater than or equal constraint
            gt: Greater than constraint
            le: Less than or equal constraint
            lt: Less than constraint
            optional: Whether the field is optional or required
            fail_test: Whether the test should expect a failure
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: integer(
                ge=ge,
                gt=gt,
                le=le,
                lt=lt,
            )  # type: ignore

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: None | (
                integer(
                    ge=ge,
                    gt=gt,
                    le=le,
                    lt=lt,
                )
            )  # type: ignore

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param([1234], [1234], False, False, id='pass-required-array-input'),
            # required, empty input
            pytest.param([], [], False, False, id='pass-required-empty-array'),
            # optional, empty input
            pytest.param([], [], True, False, id='pass-optional-empty-array'),
            # optional, null input
            pytest.param(None, None, True, False, id='pass-optional-null-input'),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(None, None, False, True, id='fail-required-null-input'),
        ],
    )
    def test_field_model_integer_array_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Integer field type with array inputs.

        This test validates Integer array field type functionality including array processing,
        empty array handling, and optional array field scenarios.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications

        Args:
            input_value: The input value to test
            expected: The expected output value after processing
            optional: Whether the field is optional or required
            fail_test: Whether the test should expect a failure
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: list[Integer]

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: list[Integer] | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='StringArray',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        'input_value,expected,input_type,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, int input
            pytest.param(1234, [1234], 'String', False, False, id='pass-required-int-to-array'),
            # required, array input
            pytest.param(
                [1234], [1234], 'StringArray', False, False, id='pass-required-array-input'
            ),
            # required, string input
            pytest.param(
                '1234', [1234], 'String', False, False, id='pass-required-string-to-array'
            ),
            # required, array input
            pytest.param(
                ['1234'], [1234], 'StringArray', False, False, id='pass-required-string-array'
            ),
            # required, empty array input
            pytest.param([], [], 'StringArray', False, False, id='pass-required-empty-array'),
            # optional, empty array input
            pytest.param([], [], 'StringArray', True, False, id='pass-optional-empty-array'),
            # optional, null input
            pytest.param(None, [], 'String', True, False, id='pass-optional-null-to-array'),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(None, None, 'String', False, True, id='fail-required-null-input'),
            # required, empty string input
            pytest.param('', [''], 'String', False, True, id='fail-required-empty-string'),
            # optional, empty string input
            pytest.param('', [''], 'String', True, True, id='fail-optional-empty-string'),
        ],
    )
    def test_field_model_integer_union_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Integer field type with union and always_array validator.

        This test validates Integer union field type functionality with the always_array
        validator, ensuring single values are converted to arrays and array inputs are preserved.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications

        Args:
            input_value: The input value to test
            expected: The expected output value after processing
            input_type: The type of input data (String or StringArray)
            optional: Whether the field is optional or required
            fail_test: Whether the test should expect a failure
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: Integer | list[Integer]

            _always_array = field_validator('my_data')(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: Integer | list[Integer] | None

            _always_array = field_validator('my_data')(always_array())

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type=input_type,
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

"""TcEx Framework Module"""

# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic.v1 import BaseModel, validator

# first-party
from tcex.input.field_type import Integer, always_array, integer
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


# pylint: disable=no-self-argument
class TestInputsFieldTypes(InputTest):
    """Test TcEx String Field Model Tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, int input
            (1234, 1234, False, False),
            # required, string input
            ('1234', 1234, False, False),
            # optional, null input
            (None, None, True, False),
            #
            # Fail Testing
            #
            # required, empty input
            ('abc', '', False, True),
            # required, empty input
            ('', '', False, True),
            # optional, empty input
            ('', '', True, True),
            # required, null input
            (None, None, False, True),
        ],
    )
    def test_field_model_integer_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
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
            (1234, 1234, None, None, None, None, False, False),
            # optional, null input
            (None, None, None, None, None, None, True, False),
            # required, normal input, ge=1000
            (1234, 1234, 1000, None, None, None, False, False),
            # required, normal input, gt=1000
            (1234, 1234, None, 1000, None, None, False, False),
            # required, normal input, le=2000
            (1234, 1234, None, None, 2000, None, False, False),
            # required, normal input, lt=2000
            (1234, 1234, None, None, None, 2000, False, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, True, None, None, None, False, True),
            # required, empty input
            ('', None, False, None, None, None, False, True),
            # required, normal input, ge=2000
            (1234, 1234, 2000, None, None, None, False, True),
            # required, normal input, gt=2000
            (1234, 1234, None, 2000, None, None, False, True),
            # required, normal input, le=1000
            (1234, 1234, None, None, 1000, None, False, True),
            # required, normal input, lt=1000
            (1234, 1234, None, None, None, 1000, False, True),
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
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
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
            ([1234], [1234], False, False),
            # required, empty input
            ([], [], False, False),
            # optional, empty input
            ([], [], True, False),
            # optional, null input
            (None, None, True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, False, True),
        ],
    )
    def test_field_model_integer_array_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
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
            (1234, [1234], 'String', False, False),
            # required, array input
            ([1234], [1234], 'StringArray', False, False),
            # required, string input
            ('1234', [1234], 'String', False, False),
            # required, array input
            (['1234'], [1234], 'StringArray', False, False),
            # required, empty array input
            ([], [], 'StringArray', False, False),
            # optional, empty array input
            ([], [], 'StringArray', True, False),
            # optional, null input
            (None, [], 'String', True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, 'String', False, True),
            # required, empty string input
            ('', [''], 'String', False, True),
            # optional, empty string input
            ('', [''], 'String', True, True),
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
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: Integer | list[Integer]

            _always_array = validator('my_data', allow_reuse=True)(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: Integer | list[Integer] | None

            _always_array = validator('my_data', allow_reuse=True)(always_array())

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

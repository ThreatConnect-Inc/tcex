"""TcEx Framework Module"""

# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic.v1 import BaseModel, validator

# first-party
from tcex.input.field_type import Binary, always_array, binary, conditional_required
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


# pylint: disable=no-self-argument
class TestInputsFieldTypes(InputTest):
    """Test TcEx String Field Model Tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        cached_property._reset()
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            (b'bytes', b'bytes', False, False),
            # required, empty input
            (b'', b'', False, False),
            # optional, empty input
            (b'', b'', True, False),
            # optional, null input
            (None, None, True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, False, True),
        ],
    )
    def test_field_model_binary_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: Binary

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: Binary | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='Binary',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        (
            'input_value,expected,allow_empty,conditional_required_rules,'
            'max_length,min_length,optional,fail_test'
        ),
        [
            #
            # Pass Testing
            #
            # required, normal input
            (b'bytes', b'bytes', True, None, None, None, False, False),
            # required, empty input
            (b'', b'', True, None, None, None, False, False),
            # optional, empty input
            (b'', b'', True, None, None, None, True, False),
            # optional, null input
            (None, None, True, None, None, None, True, False),
            # required, normal input, max_length=10
            (b'bytes', b'bytes', True, None, 10, None, False, False),
            # optional, normal input, max_length=10
            (b'bytes', b'bytes', True, None, 10, None, True, False),
            # required, normal input, min_length=2
            (b'bytes', b'bytes', True, None, None, 2, False, False),
            # optional, normal input, min_length=2
            (b'bytes', b'bytes', True, None, None, 2, True, False),
            # optional, null input, conditional_required=True
            (
                None,
                None,
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'optional'}],
                None,
                None,
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, True, None, None, None, False, True),
            # required, empty input, allow_empty=False
            (b'', None, False, None, None, None, False, True),
            # required, normal input, conditional_required=True
            (
                b'',
                b'bytes',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                False,
                True,
            ),
            # required, null input, conditional_required=True
            (
                None,
                'string',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                False,
                True,
            ),
            # required, normal input, max_length=2
            (b'bytes', b'bytes', True, None, 2, None, False, True),
            # optional, normal input, max_length=2
            (b'bytes', b'bytes', True, None, 2, None, True, True),
            # required, normal input, min_length=10
            (b'bytes', b'bytes', True, None, None, 10, False, True),
            # optional, normal input, min_length=10
            (b'bytes', b'bytes', True, None, None, 10, True, True),
        ],
    )
    def test_field_model_binary_custom_input(
        self,
        input_value: str,
        expected: str,
        allow_empty: bool,
        conditional_required_rules: dict[str, str],
        max_length: int,
        min_length: int,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            conditional: str | None = 'required'
            my_data: binary(
                allow_empty=allow_empty,
                max_length=max_length,
                min_length=min_length,
            )  # type: ignore

            _conditional_required = validator('my_data', allow_reuse=True, always=True, pre=True)(
                conditional_required(rules=conditional_required_rules)  # type: ignore
            )

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            conditional: str | None = 'required'
            my_data: None | (
                binary(
                    allow_empty=allow_empty,
                    max_length=max_length,
                    min_length=min_length,
                )
            )  # type: ignore

            _conditional_required = validator('my_data', allow_reuse=True, always=True, pre=True)(
                conditional_required(rules=conditional_required_rules)  # type: ignore
            )

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='Binary',
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
            ([b'bytes'], [b'bytes'], False, False),
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
    def test_field_model_binary_array_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: list[Binary]

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: list[Binary] | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='BinaryArray',
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
            # required, bytes input
            (b'bytes', [b'bytes'], 'Binary', False, False),
            # required, array input
            ([b'bytes'], [b'bytes'], 'BinaryArray', False, False),
            # required, empty input
            (b'', [b''], 'Binary', False, False),
            # required, empty input
            ([], [], 'BinaryArray', False, False),
            # optional, empty input
            (b'', [b''], 'Binary', True, False),
            # optional, null input
            (None, [], 'Binary', True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, 'Binary', False, True),
        ],
    )
    def test_field_model_binary_union_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: Binary | list[Binary]

            _always_array = validator('my_data', allow_reuse=True)(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: Binary | None | list[Binary] | None

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

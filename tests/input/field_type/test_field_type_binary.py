"""TestInputsFieldTypes for testing Binary field type functionality.

This module contains comprehensive test cases for the Binary field type implementation in TcEx,
including validation of required/optional fields, custom validators, array and union types, and error handling.

Classes:
    TestInputsFieldTypes: Test class for Binary field type validation

TcEx Module Tested: tcex.input.field_type.Binary
"""


from collections.abc import Callable
from typing import Any


import pytest
from pydantic import BaseModel, field_validator


from tcex.input.field_type import (Binary, always_array, binary,
                                   conditional_required)
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypes(InputTest):
    """TestInputsFieldTypes for comprehensive Binary field type testing.

    This class provides extensive test coverage for the Binary field type, including validation
    of required/optional fields, custom validators, array and union types, and error handling.

    Fixtures:
        playbook_app: Mock application fixture for testing TcEx functionality
    """

    def setup_method(self) -> None:
        """Configure setup before all tests."""
        cached_property._reset()
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            pytest.param(b'bytes', b'bytes', False, False, id='pass-required-bytes-input'),
            pytest.param(b'', b'', False, False, id='pass-required-empty-bytes'),
            pytest.param(b'', b'', True, False, id='pass-optional-empty-bytes'),
            pytest.param(None, None, True, False, id='pass-optional-none-input'),
            pytest.param(None, None, False, True, id='fail-required-none-input'),
        ],
    )
    def test_field_model_binary_input(
        self,
        input_value: Any,
        expected: Any,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Binary field type with basic validation.

        Tests the basic Binary field type functionality including required vs optional field
        behaviors, empty bytes handling, and None value validation.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
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
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                None,
                None,
                False,
                False,
                id='pass-required-bytes-input',
            ),
            pytest.param(
                b'', b'', True, None, None, None, False, False, id='pass-required-empty-bytes'
            ),
            pytest.param(
                b'', b'', True, None, None, None, True, False, id='pass-optional-empty-bytes'
            ),
            pytest.param(
                None, None, True, None, None, None, True, False, id='pass-optional-none-input'
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                10,
                None,
                False,
                False,
                id='pass-required-max-length-10',
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                10,
                None,
                True,
                False,
                id='pass-optional-max-length-10',
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                None,
                2,
                False,
                False,
                id='pass-required-min-length-2',
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                None,
                2,
                True,
                False,
                id='pass-optional-min-length-2',
            ),
            pytest.param(
                None,
                None,
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'optional'}],
                None,
                None,
                True,
                False,
                id='pass-optional-conditional-required',
            ),
            pytest.param(
                None, None, True, None, None, None, False, True, id='fail-required-none-input'
            ),
            pytest.param(
                b'',
                None,
                False,
                None,
                None,
                None,
                False,
                True,
                id='fail-required-empty-not-allowed',
            ),
            pytest.param(
                b'',
                b'bytes',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                False,
                True,
                id='fail-required-conditional-empty',
            ),
            pytest.param(
                None,
                'string',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                False,
                True,
                id='fail-required-conditional-none',
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                2,
                None,
                False,
                True,
                id='fail-required-max-length-exceeded',
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                2,
                None,
                True,
                True,
                id='fail-optional-max-length-exceeded',
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                None,
                10,
                False,
                True,
                id='fail-required-min-length-not-met',
            ),
            pytest.param(
                b'bytes',
                b'bytes',
                True,
                None,
                None,
                10,
                True,
                True,
                id='fail-optional-min-length-not-met',
            ),
        ],
    )
    def test_field_model_binary_custom_input(
        self,
        input_value: Any,
        expected: Any,
        allow_empty: bool,
        conditional_required_rules: Any,
        max_length: int | None,
        min_length: int | None,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Binary field type with custom validators and constraints.

        Tests the Binary field type with advanced functionality including allow_empty settings,
        conditional_required validators, max_length and min_length constraints, and various
        edge cases for validation.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            conditional: str | None = 'required'
            my_data: binary(
                allow_empty=allow_empty,
                max_length=max_length,
                min_length=min_length,
            )  # type: ignore

            _conditional_required = field_validator('my_data', mode='before')(
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

            _conditional_required = field_validator('my_data', mode='before')(
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
            pytest.param([b'bytes'], [b'bytes'], False, False, id='pass-required-bytes-array'),
            pytest.param([], [], False, False, id='pass-required-empty-array'),
            pytest.param([], [], True, False, id='pass-optional-empty-array'),
            pytest.param(None, None, True, False, id='pass-optional-none-input'),
            pytest.param(None, None, False, True, id='fail-required-none-input'),
        ],
    )
    def test_field_model_binary_array_input(
        self,
        input_value: Any,
        expected: Any,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Binary field type with array inputs.

        Tests the Binary field type as an array (list[Binary]) including required vs optional
        behaviors, empty array handling, and None value validation for array types.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
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
            pytest.param(
                b'bytes', [b'bytes'], 'Binary', False, False, id='pass-required-bytes-to-array'
            ),
            pytest.param(
                [b'bytes'], [b'bytes'], 'BinaryArray', False, False, id='pass-required-array-input'
            ),
            pytest.param(
                b'', [b''], 'Binary', False, False, id='pass-required-empty-bytes-to-array'
            ),
            pytest.param([], [], 'BinaryArray', False, False, id='pass-required-empty-array'),
            pytest.param(
                b'', [b''], 'Binary', True, False, id='pass-optional-empty-bytes-to-array'
            ),
            pytest.param(None, [], 'Binary', True, False, id='pass-optional-none-to-empty-array'),
            pytest.param(None, None, 'Binary', False, True, id='fail-required-none-input'),
        ],
    )
    def test_field_model_binary_union_input(
        self,
        input_value: Any,
        expected: Any,
        input_type: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Binary field type with union types and always_array validator.

        Tests the Binary field type as a union (Binary | list[Binary]) with the always_array
        validator, which converts single Binary values to arrays and handles various input types.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: Binary | list[Binary]

            _always_array = field_validator('my_data')(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: Binary | None | list[Binary]

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

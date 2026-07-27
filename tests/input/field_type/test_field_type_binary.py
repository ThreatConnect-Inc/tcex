"""TestInputsFieldTypes for testing Binary field type functionality.

This module contains comprehensive test cases for the Binary field type implementation in TcEx,
including validation of required/optional fields, custom validators, array and union types, and error handling.

Classes:
    TestInputsFieldTypes: Test class for Binary field type validation

TcEx Module Tested: tcex.input.field_type.Binary
"""

from collections.abc import Callable
from typing import Annotated, Any

import pytest
from pydantic import BaseModel, ValidationError, field_validator
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING

from tcex.input.field_type import Binary, always_array, binary, conditional_required
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property


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


class TestBinaryAnnotated:
    """Test Binary field type via Annotated[bytes, binary(...)] syntax.

    Exercises the annotated-metadata chaining contract so that
    binary(...) factory constraints take effect when the type is written
    as Annotated[bytes, binary(...)] rather than as a bare Binary subclass.
    """

    def setup_method(self) -> None:
        """Configure setup before each test."""
        cached_property._reset()  # noqa: SLF001
        scoped_property._reset()  # noqa: SLF001

    @pytest.mark.parametrize(
        argnames='input_value,expected,should_fail',
        argvalues=[
            pytest.param(
                # valid bytes well within max_length=20
                b'hello',
                b'hello',
                False,
                id='pass-valid-bytes-within-max-length',
            ),
            pytest.param(
                # 21-byte value exceeds max_length=20
                b'toolongbytes123456789',
                None,
                True,
                id='fail-exceeds-max-length',
            ),
            pytest.param(
                # empty bytes rejected by allow_empty=False
                b'',
                None,
                True,
                id='fail-empty-bytes-not-allowed',
            ),
        ],
    )
    def test_binary_annotated_constraints(
        self,
        input_value: bytes,
        expected: bytes | None,
        should_fail: bool,
    ) -> None:
        """Test Binary via Annotated with max_length and allow_empty constraints."""

        class M(BaseModel):
            x: Annotated[bytes, binary(max_length=20, allow_empty=False)]

        if should_fail:
            with pytest.raises(ValidationError):
                M(x=input_value)
        else:
            result = M(x=input_value)
            assert result.x == expected, f'Expected {expected!r}, got {result.x!r}'

    @pytest.mark.parametrize(
        argnames='input_value,expected',
        argvalues=[
            pytest.param(
                # leading and trailing whitespace bytes are removed by strip=True
                b'  hello  ',
                b'hello',
                id='pass-strip-trims-whitespace-bytes',
            ),
            pytest.param(
                # bytes with no surrounding whitespace are unchanged
                b'hello',
                b'hello',
                id='pass-strip-no-whitespace-unchanged',
            ),
        ],
    )
    def test_binary_annotated_strip(
        self,
        input_value: bytes,
        expected: bytes,
    ) -> None:
        """Test Binary via Annotated with strip=True trims surrounding whitespace bytes."""

        class M(BaseModel):
            x: Annotated[bytes, binary(strip=True)]

        result = M(x=input_value)
        assert result.x == expected, f'Expected {expected!r}, got {result.x!r}'

    def test_binary_annotated_optional_none(self) -> None:
        """Test Binary via Annotated accepts None for an optional field."""

        class M(BaseModel):
            x: Annotated[bytes, binary()] | None = None

        result = M(x=None)
        assert result.x is None

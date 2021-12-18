"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

# third-party
import pytest
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_models import Binary, always_array, binary
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_models.utils import InputTest

if TYPE_CHECKING:
    # third-party
    from pydantic.fields import ModelField

    # first-party
    from tests.mock_app import MockApp


# pylint: disable=no-self-argument, no-self-use
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
        playbook_app: 'MockApp',
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Binary

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Optional[Binary]

        self._type_validation(
            PytestModel,
            input_name='my_data',
            input_value=input_value,
            input_type='Binary',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        (
            'input_value,expected,allow_empty,conditional_required,'
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
            (None, None, True, {'conditional': 'optional'}, None, None, True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, True, None, None, None, False, True),
            # required, empty input, allow_empty=False
            (b'', None, False, None, None, None, False, True),
            # required, normal input, conditional_required=True
            (b'', b'bytes', True, {'conditional': 'required'}, None, None, False, True),
            # required, null input, conditional_required=True
            (None, 'string', True, {'conditional': 'required'}, None, None, False, True),
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
        conditional_required: Dict[str, str],
        max_length: int,
        min_length: int,
        optional: bool,
        fail_test: bool,
        playbook_app: 'MockApp',
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                conditional: Optional[str] = 'required'
                my_data: binary(
                    allow_empty=allow_empty,
                    # conditional_required=conditional_required,
                    max_length=max_length,
                    min_length=min_length,
                )

                @validator('my_data', allow_reuse=True, always=True, pre=True)
                def _conditional_required(cls, v: str, field: 'ModelField', values: Dict[str, Any]):
                    if conditional_required:
                        for conditional_key, conditional_value in conditional_required.items():
                            if values.get(conditional_key) == conditional_value and not v:
                                raise ValueError(
                                    f'Value is required for field "{field.name}" when '
                                    f'"{conditional_key}" equals "{conditional_value}".'
                                )
                    return v

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                conditional: Optional[str] = 'required'
                my_data: Optional[
                    binary(
                        allow_empty=allow_empty,
                        # conditional_required=conditional_required,
                        max_length=max_length,
                        min_length=min_length,
                    )
                ]

                @validator('my_data', allow_reuse=True, always=True, pre=True)
                def _conditional_required(cls, v: str, field: 'ModelField', values: Dict[str, Any]):
                    if conditional_required:
                        for conditional_key, conditional_value in conditional_required.items():
                            if values.get(conditional_key) == conditional_value and not v:
                                raise ValueError(
                                    f'Value is required for field "{field.name}" when '
                                    f'"{conditional_key}" equals "{conditional_value}".'
                                )
                    return v

        self._type_validation(
            PytestModel,
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
        playbook_app: 'MockApp',
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: List[Binary]

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Optional[List[Binary]]

        self._type_validation(
            PytestModel,
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
        playbook_app: 'MockApp',
    ):
        """Test Binary field type.

        Playbook Data Type: Binary
        Validation: Not null
        """

        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Union[Binary, List[Binary]]

                _always_array = validator('my_data', allow_reuse=True)(always_array)

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Union[Optional[Binary], Optional[List[Binary]]]

                _always_array = validator('my_data', allow_reuse=True)(always_array)

        self._type_validation(
            PytestModel,
            input_name='my_data',
            input_value=input_value,
            input_type=input_type,
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

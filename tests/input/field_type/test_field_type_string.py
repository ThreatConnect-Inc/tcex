"""TestInputsFieldTypes for String field type validation.

This module contains comprehensive test cases for the String field type functionality
within the TcEx Framework, including validation of single strings, arrays, custom
configurations, and complex nested reference resolution scenarios.

Classes:
    TestInputsFieldTypes: Test cases for String field type validation

TcEx Module Tested: tcex.input.field_type.string
"""

# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel, field_validator

# first-party
from tcex.input.field_type import (String, always_array, conditional_required,
                                   string)
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypes(InputTest):
    """TestInputsFieldTypes for String field type validation.

    This class provides comprehensive test coverage for String field types including
    validation of single strings, arrays, custom configurations with constraints,
    union types, and complex nested reference resolution scenarios.

    Fixtures:
        playbook_app: MockApp instance for testing field validation
    """

    def setup_method(self) -> None:
        """Configure setup before all tests."""
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param('string', 'string', False, False, id='pass-required-normal-string'),
            # required, empty input
            pytest.param('', '', False, False, id='pass-required-empty-string'),
            # optional, empty input
            pytest.param('', '', True, False, id='pass-optional-empty-string'),
            # optional, null input
            pytest.param(None, None, True, False, id='pass-optional-null-input'),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(None, None, False, True, id='fail-required-null-input'),
        ],
    )
    def test_field_model_string_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test String field type with basic validation scenarios.

        This test validates the String field type with various input scenarios including
        normal strings, empty strings, and null values for both required and optional fields.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: String

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: String | None

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
        (
            'input_value,expected,allow_empty,conditional_required_rules,'
            'max_length,min_length,regex,optional,fail_test'
        ),
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param(
                'string',
                'string',
                True,
                None,
                None,
                None,
                None,
                False,
                False,
                id='pass-required-normal-string',
            ),
            # required, empty input
            pytest.param(
                '',
                '',
                True,
                None,
                None,
                None,
                None,
                False,
                False,
                id='pass-required-empty-allow-empty',
            ),
            # optional, empty input
            pytest.param(
                '',
                '',
                True,
                None,
                None,
                None,
                None,
                True,
                False,
                id='pass-optional-empty-allow-empty',
            ),
            # optional, null input
            pytest.param(
                None, None, True, None, None, None, None, True, False, id='pass-optional-null-input'
            ),
            # required, normal input, max_length=10
            pytest.param(
                'string',
                'string',
                True,
                None,
                10,
                None,
                None,
                False,
                False,
                id='pass-required-max-length-valid',
            ),
            # optional, normal input, max_length=10
            pytest.param(
                'string',
                'string',
                True,
                None,
                10,
                None,
                None,
                True,
                False,
                id='pass-optional-max-length-valid',
            ),
            # required, normal input, min_length=2
            pytest.param(
                'string',
                'string',
                True,
                None,
                None,
                2,
                None,
                False,
                False,
                id='pass-required-min-length-valid',
            ),
            # optional, normal input, min_length=2
            pytest.param(
                'string',
                'string',
                True,
                None,
                None,
                2,
                None,
                True,
                False,
                id='pass-optional-min-length-valid',
            ),
            # required, normal input, regex=string
            pytest.param(
                'string',
                'string',
                True,
                None,
                None,
                None,
                r'^string$',
                True,
                False,
                id='pass-required-regex-match',
            ),
            # optional, null input, conditional_required=True
            pytest.param(
                None,
                None,
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'optional'}],
                None,
                None,
                None,
                True,
                False,
                id='pass-optional-conditional-not-required',
            ),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(
                None, None, True, None, None, None, None, False, True, id='fail-required-null-input'
            ),
            # required, empty input, allow_empty=False
            pytest.param(
                '',
                None,
                False,
                None,
                None,
                None,
                None,
                False,
                True,
                id='fail-required-empty-disallow-empty',
            ),
            # required, empty input, conditional_required=True
            pytest.param(
                '',
                'string',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                None,
                False,
                True,
                id='fail-required-empty-conditional-required',
            ),
            # required, null input, conditional_required=True
            pytest.param(
                None,
                'string',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                None,
                False,
                True,
                id='fail-required-null-conditional-required',
            ),
            # required, normal input, max_length=2
            pytest.param(
                'string',
                'string',
                True,
                None,
                2,
                None,
                None,
                False,
                True,
                id='fail-required-max-length-exceeded',
            ),
            # optional, normal input, max_length=2
            pytest.param(
                'string',
                'string',
                True,
                None,
                2,
                None,
                None,
                True,
                True,
                id='fail-optional-max-length-exceeded',
            ),
            # required, normal input, min_length=10
            pytest.param(
                'string',
                'string',
                True,
                None,
                None,
                10,
                None,
                False,
                True,
                id='fail-required-min-length-not-met',
            ),
            # optional, normal input, min_length=10
            pytest.param(
                'string',
                'string',
                True,
                None,
                None,
                10,
                None,
                True,
                True,
                id='fail-optional-min-length-not-met',
            ),
            # required, normal input, regex=string
            pytest.param(
                'string',
                'string',
                True,
                None,
                None,
                None,
                r'^string-extra$',
                True,
                True,
                id='fail-required-regex-no-match',
            ),
        ],
    )
    def test_field_model_string_custom_input(
        self,
        input_value: str,
        expected: str,
        allow_empty: bool,
        conditional_required_rules: list[dict[str, str]] | None,
        max_length: int,
        min_length: int,
        regex: str | None,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test String field type with custom configuration options.

        This test validates the String field type with custom configuration options including
        allow_empty, conditional_required rules, max_length, min_length, and regex constraints
        for both required and optional fields.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            conditional: str = 'required'
            my_data: string(
                allow_empty=allow_empty,
                max_length=max_length,
                min_length=min_length,
                regex=regex,
            )  # type: ignore

            _conditional_required = field_validator('my_data', mode='before')(
                conditional_required(rules=conditional_required_rules or [])
            )

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            conditional: str = 'required'
            my_data: None | (
                string(
                    allow_empty=allow_empty,
                    max_length=max_length,
                    min_length=min_length,
                    regex=regex,
                )
            )  # type: ignore

            _conditional_required = field_validator('my_data', mode='before')(
                conditional_required(rules=conditional_required_rules or [])
            )

        if optional is False:
            pytest_model = PytestModelRequired
        else:
            pytest_model = PytestModelOptional

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
            pytest.param(['string'], ['string'], False, False, id='pass-required-string-array'),
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
    def test_field_model_string_array_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test String field type with array validation.

        This test validates the String field type in array format, testing scenarios
        with valid string arrays, empty arrays, and null values for both required
        and optional fields.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: list[String]

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: list[String] | None

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
            # required, string input
            pytest.param(
                'string', ['string'], 'String', False, False, id='pass-required-string-to-array'
            ),
            # required, array input
            pytest.param(
                ['string'], ['string'], 'StringArray', False, False, id='pass-required-array-input'
            ),
            # required, empty string input
            pytest.param('', [], 'String', False, False, id='pass-required-empty-string-to-array'),
            # required, empty array input
            pytest.param([], [], 'StringArray', False, False, id='pass-required-empty-array'),
            # optional, empty string input
            pytest.param('', [], 'String', True, False, id='pass-optional-empty-string-to-array'),
            # optional, empty array input
            pytest.param([], [], 'StringArray', True, False, id='pass-optional-empty-array'),
            # optional, null input
            pytest.param(None, [], 'String', True, False, id='pass-optional-null-to-array'),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(None, None, 'String', False, True, id='fail-required-null-input'),
        ],
    )
    def test_field_model_string_union_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test String field type with union type and always_array validation.

        This test validates String union types that can accept both single strings and
        arrays, with always_array validation ensuring consistent array output format.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: String | list[String]

            _always_array = field_validator('my_data')(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: String | list[String] | None

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

    @pytest.mark.parametrize(
        ('nested_reference,nested_value,value,expected_value'),
        [
            pytest.param(
                '#App:1234:my_ref!String',
                'nested string',
                'string with nested string: #App:1234:my_ref!String',
                'string with nested string: nested string',
                id='pass-embedded-string-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!StringArray',
                ['nested string'],
                'string with nested value: #App:1234:my_ref!StringArray',
                'string with nested value: ["nested string"]',
                id='pass-embedded-string-array-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!Binary',
                b'nested string',
                'string with nested string: #App:1234:my_ref!Binary',
                'string with nested string: <binary>',
                id='pass-embedded-binary-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!BinaryArray',
                [b'nested string'],
                'string with nested string: #App:1234:my_ref!BinaryArray',
                'string with nested string: <binary>',
                id='pass-embedded-binary-array-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
                'string with nested string: #App:1234:my_ref!KeyValue',
                'string with nested string: {"key": "key", "value": "value", "type": "any"}',
                id='pass-embedded-key-value-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
                'string with nested string: #App:1234:my_ref!KeyValueArray',
                'string with nested string: [{"key": "key", "value": "value", "type": "any"}]',
                id='pass-embedded-key-value-array-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!TCEntity',
                {'id': '1', 'value': '1.1.1.1', 'type': 'Address'},
                'string with nested string: #App:1234:my_ref!TCEntity',
                'string with nested string: {"id": "1", "value": "1.1.1.1", "type": "Address"}',
                id='pass-embedded-tc-entity-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!TCEntityArray',
                [{'id': '1', 'value': '1.1.1.1', 'type': 'Address'}],
                'string with nested string: #App:1234:my_ref!TCEntityArray',
                'string with nested string: [{"id": "1", "value": "1.1.1.1", "type": "Address"}]',
                id='pass-embedded-tc-entity-array-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!String',
                None,
                'string with nested string: #App:1234:my_ref!String',
                'string with nested string: <null>',
                id='pass-embedded-null-reference',
            ),
        ],
    )
    def test_field_type_string_with_nested_reference(
        self,
        nested_reference,
        nested_value,
        value,
        expected_value,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test String field type with complex nested reference resolution.

        This test validates the String field type with nested variable references embedded
        within strings, testing various data types including strings, arrays, binary data,
        KeyValues, TCEntities, and null reference handling.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_data: String

        config_data = {'my_data': '#App:1234:my_data!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_ref', nested_reference, nested_value, tcex)
        self._stage_key_value(
            'my_data',
            '#App:1234:my_data!String',
            value,
            tcex,
        )
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.model.my_data == expected_value  # type: ignore

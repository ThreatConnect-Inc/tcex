"""Testing TcEx Input module field types."""
# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_type import String, always_array, conditional_required, string
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
            # required, normal input
            ('string', 'string', False, False),
            # required, empty input
            ('', '', False, False),
            # optional, empty input
            ('', '', True, False),
            # optional, null input
            (None, None, True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, False, True),
        ],
    )
    def test_field_model_string_input(
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
            ('string', 'string', True, None, None, None, None, False, False),
            # required, empty input
            ('', '', True, None, None, None, None, False, False),
            # optional, empty input
            ('', '', True, None, None, None, None, True, False),
            # optional, null input
            (None, None, True, None, None, None, None, True, False),
            # required, normal input, max_length=10
            ('string', 'string', True, None, 10, None, None, False, False),
            # optional, normal input, max_length=10
            ('string', 'string', True, None, 10, None, None, True, False),
            # required, normal input, min_length=2
            ('string', 'string', True, None, None, 2, None, False, False),
            # optional, normal input, min_length=2
            ('string', 'string', True, None, None, 2, None, True, False),
            # required, normal input, regex=string
            ('string', 'string', True, None, None, None, r'^string$', True, False),
            # optional, null input, conditional_required=True
            (
                None,
                None,
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'optional'}],
                None,
                None,
                None,
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, True, None, None, None, None, False, True),
            # required, empty input, allow_empty=False
            ('', None, False, None, None, None, None, False, True),
            # required, empty input, conditional_required=True
            (
                '',
                'string',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
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
                None,
                False,
                True,
            ),
            # required, normal input, max_length=2
            ('string', 'string', True, None, 2, None, None, False, True),
            # optional, normal input, max_length=2
            ('string', 'string', True, None, 2, None, None, True, True),
            # required, normal input, min_length=10
            ('string', 'string', True, None, None, 10, None, False, True),
            # optional, normal input, min_length=10
            ('string', 'string', True, None, None, 10, None, True, True),
            # required, normal input, regex=string
            ('string', 'string', True, None, None, None, r'^string-extra$', True, True),
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
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
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

            _conditional_required = validator('my_data', allow_reuse=True, always=True, pre=True)(
                conditional_required(rules=conditional_required_rules)  # type: ignore
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
            (['string'], ['string'], False, False),
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
    def test_field_model_string_array_input(
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
            ('string', ['string'], 'String', False, False),
            # required, array input
            (['string'], ['string'], 'StringArray', False, False),
            # required, empty string input
            ('', [], 'String', False, False),
            # required, empty array input
            ([], [], 'StringArray', False, False),
            # optional, empty string input
            ('', [], 'String', True, False),
            # optional, empty array input
            ([], [], 'StringArray', True, False),
            # optional, null input
            (None, [], 'String', True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, 'String', False, True),
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
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: String | list[String]

            _always_array = validator('my_data', allow_reuse=True)(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: String | list[String] | None

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

    @pytest.mark.parametrize(
        ('nested_reference,nested_value,value,expected_value'),
        [
            (
                '#App:1234:my_ref!String',
                'nested string',
                'string with nested string: #App:1234:my_ref!String',
                'string with nested string: nested string',
            ),
            (
                '#App:1234:my_ref!StringArray',
                ['nested string'],
                'string with nested value: #App:1234:my_ref!StringArray',
                'string with nested value: ["nested string"]',
            ),
            (
                '#App:1234:my_ref!Binary',
                b'nested string',
                'string with nested string: #App:1234:my_ref!Binary',
                'string with nested string: <binary>',
            ),
            (
                '#App:1234:my_ref!BinaryArray',
                [b'nested string'],
                'string with nested string: #App:1234:my_ref!BinaryArray',
                'string with nested string: <binary>',
            ),
            (
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
                'string with nested string: #App:1234:my_ref!KeyValue',
                'string with nested string: {"key": "key", "value": "value", "type": "any"}',
            ),
            (
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
                'string with nested string: #App:1234:my_ref!KeyValueArray',
                'string with nested string: [{"key": "key", "value": "value", "type": "any"}]',
            ),
            (
                '#App:1234:my_ref!TCEntity',
                {'id': '1', 'value': '1.1.1.1', 'type': 'Address'},
                'string with nested string: #App:1234:my_ref!TCEntity',
                'string with nested string: {"id": "1", "value": "1.1.1.1", "type": "Address"}',
            ),
            (
                '#App:1234:my_ref!TCEntityArray',
                [{'id': '1', 'value': '1.1.1.1', 'type': 'Address'}],
                'string with nested string: #App:1234:my_ref!TCEntityArray',
                'string with nested string: [{"id": "1", "value": "1.1.1.1", "type": "Address"}]',
            ),
            (
                '#App:1234:my_ref!String',
                None,
                'string with nested string: #App:1234:my_ref!String',
                'string with nested string: <null>',
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
    ):
        """Test String field type with nested reference.

        Args:
            nested_reference: nested variable reference found within string
            nested_value: the value that nested_reference should resolve to
            value: the String value exactly as passed in from the UI
            expected_value: The String value as passed in from the UI after nested reference
            is resolved
            playbook_app (fixture): An instance of MockApp.
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

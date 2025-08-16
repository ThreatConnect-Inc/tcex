"""TestInputsFieldTypeKeyValue for KeyValue field type validation.

This module contains comprehensive test cases for the KeyValue field type functionality
within the TcEx Framework, including validation of simple key-value pairs and complex
nested reference resolution scenarios.

Classes:
    TestInputsFieldTypeKeyValue: Test cases for KeyValue field type validation

TcEx Module Tested: tcex.input.field_type.key_value
"""

# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel

# first-party
from tcex.input.field_type import KeyValue, TCEntity
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypeKeyValue(InputTest):
    """TestInputsFieldTypeKeyValue for KeyValue field type validation.

    This class provides comprehensive test coverage for KeyValue field types including
    validation of simple key-value pairs and complex nested reference resolution with
    various data types and edge cases.

    Fixtures:
        playbook_app: MockApp instance for testing field validation
    """

    def setup_method(self) -> None:
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    @pytest.mark.parametrize(
        ('input_value,expected,optional,fail_test'),
        [
            pytest.param(
                {'key': 'my_key', 'value': 'my_string', 'type': 'string'},
                {'key': 'my_key', 'value': 'my_string', 'type': 'string'},
                False,
                False,
                id='pass-required-valid-key-value',
            ),
            pytest.param(
                None,
                None,
                True,
                False,
                id='pass-optional-null-input',
            ),
        ],
    )
    def test_field_type_key_value_simple(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test KeyValue field type with simple key-value pair validation.

        This test validates the KeyValue field type with basic key-value pair structures
        including required and optional field scenarios.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValue

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValue | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_key_value',
            input_value=input_value,
            input_type='KeyValue',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        ('nested_reference,nested_value,value,expected_value'),
        [
            pytest.param(
                '#App:1234:my_ref!Binary',
                b'binary string',
                '#App:1234:my_ref!Binary',
                b'binary string',
                id='pass-direct-binary-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!BinaryArray',
                [b'binary string'],
                '#App:1234:my_ref!BinaryArray',
                [b'binary string'],
                id='pass-direct-binary-array-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!String',
                'string',
                '#App:1234:my_ref!String',
                'string',
                id='pass-direct-string-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!StringArray',
                ['string'],
                '#App:1234:my_ref!StringArray',
                ['string'],
                id='pass-direct-string-array-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
                id='pass-direct-key-value-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
                id='pass-direct-key-value-array-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!TCEntity',
                {'id': '1', 'value': '1.1.1.1', 'type': 'Address'},
                '#App:1234:my_ref!TCEntity',
                TCEntity(id='1', value='1.1.1.1', type='Address'),  # type: ignore
                id='pass-direct-tc-entity-reference',
            ),
            pytest.param(
                '#App:1234:my_ref!TCEntityArray',
                [{'id': '1', 'value': '1.1.1.1', 'type': 'Address'}],
                '#App:1234:my_ref!TCEntityArray',
                [TCEntity(id='1', value='1.1.1.1', type='Address')],  # type: ignore
                id='pass-direct-tc-entity-array-reference',
            ),
            # value is string with String variable reference
            pytest.param(
                '#App:1234:my_ref!String',
                'string',
                'String with nested ref #App:1234:my_ref!String',
                'String with nested ref string',
                id='pass-embedded-string-reference',
            ),
            # value is string with StringArray reference
            pytest.param(
                '#App:1234:my_ref!StringArray',
                ['string'],
                'String with nested ref #App:1234:my_ref!StringArray',
                'String with nested ref ["string"]',
                id='pass-embedded-string-array-reference',
            ),
            # value is string with KeyValue reference
            pytest.param(
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
                'String with nested ref #App:1234:my_ref!KeyValue',
                'String with nested ref {"key": "key", "value": "value", "type": "any"}',
                id='pass-embedded-key-value-reference',
            ),
            # value is string with KeyValueArray reference
            pytest.param(
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
                'String with nested ref #App:1234:my_ref!KeyValueArray',
                'String with nested ref [{"key": "key", "value": "value", "type": "any"}]',
                id='pass-embedded-key-value-array-reference',
            ),
            # value is string with TCEntity reference
            pytest.param(
                '#App:1234:my_ref!TCEntity',
                {'id': '1', 'value': '1.1.1.1', 'type': 'Address'},
                'String with nested ref #App:1234:my_ref!TCEntity',
                'String with nested ref {"id": "1", "value": "1.1.1.1", "type": "Address"}',
                id='pass-embedded-tc-entity-reference',
            ),
            # value is string with TCEntityArray reference
            pytest.param(
                '#App:1234:my_ref!TCEntityArray',
                [{'id': '1', 'value': '1.1.1.1', 'type': 'Address'}],
                'String with nested ref #App:1234:my_ref!TCEntityArray',
                'String with nested ref [{"id": "1", "value": "1.1.1.1", "type": "Address"}]',
                id='pass-embedded-tc-entity-array-reference',
            ),
            # value is string with reference that resolves to None
            # NOTE: need to be able to clear key value store between tests
            pytest.param(
                '#App:1234:my_ref2!String',
                None,
                'String with nested ref #App:1234:my_ref2!String',
                'String with nested ref <null>',
                id='pass-embedded-null-reference',
            ),
            # value is string with reference to binary
            # need to add exception handling in read_embedded
            pytest.param(
                '#App:1234:my_ref!Binary',
                b'binary string',
                'string with binary reference #App:1234:my_ref!Binary',
                'string with binary reference <binary>',
                id='pass-embedded-binary-reference',
            ),
        ],
    )
    def test_field_type_key_value_with_nested_reference(
        self,
        nested_reference,
        nested_value,
        value,
        expected_value,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test KeyValue field type with complex nested reference resolution.

        This test validates the KeyValue field type with nested variable references,
        testing direct references, embedded references within strings, and various
        data types including binary, arrays, and TCEntity objects.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValue

        config_data = {'my_key_value': '#App:1234:my_key_value!KeyValue'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_ref', nested_reference, nested_value, tcex)
        self._stage_key_value(
            'my_key_value',
            '#App:1234:my_key_value!KeyValue',
            {'key': 'my_key', 'value': value, 'type': 'any'},
            tcex,
        )
        tcex.inputs.add_model(PytestModel)

        if isinstance(expected_value, BaseModel):
            expected_value = expected_value.model_dump()
        if isinstance(expected_value, list) and isinstance(expected_value[0], BaseModel):
            expected_value = [ev.model_dump() for ev in expected_value]
        assert tcex.inputs.model.my_key_value.model_dump() == {  # type: ignore
            'key': 'my_key',
            'value': expected_value,
            'type': 'any',
        }

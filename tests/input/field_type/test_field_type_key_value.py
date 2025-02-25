"""TcEx Framework Module"""

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
    """Test TcEx Inputs Config."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    @pytest.mark.parametrize(
        ('input_value,expected,optional,fail_test'),
        [
            (
                {'key': 'my_key', 'value': 'my_string', 'type': 'string'},
                {'key': 'my_key', 'value': 'my_string', 'type': 'string'},
                False,
                False,
            ),
            (
                None,
                None,
                True,
                False,
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
    ):
        """Test KeyValue field type with string input."""

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
            (
                '#App:1234:my_ref!Binary',
                b'binary string',
                '#App:1234:my_ref!Binary',
                b'binary string',
            ),
            (
                '#App:1234:my_ref!BinaryArray',
                [b'binary string'],
                '#App:1234:my_ref!BinaryArray',
                [b'binary string'],
            ),
            ('#App:1234:my_ref!String', 'string', '#App:1234:my_ref!String', 'string'),
            (
                '#App:1234:my_ref!StringArray',
                ['string'],
                '#App:1234:my_ref!StringArray',
                ['string'],
            ),
            (
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
            ),
            (
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
            ),
            (
                '#App:1234:my_ref!TCEntity',
                {'id': '1', 'value': '1.1.1.1', 'type': 'Address'},
                '#App:1234:my_ref!TCEntity',
                TCEntity(**{'id': '1', 'value': '1.1.1.1', 'type': 'Address'}),  # type: ignore
            ),
            (
                '#App:1234:my_ref!TCEntityArray',
                [{'id': '1', 'value': '1.1.1.1', 'type': 'Address'}],
                '#App:1234:my_ref!TCEntityArray',
                [TCEntity(**{'id': '1', 'value': '1.1.1.1', 'type': 'Address'})],  # type: ignore
            ),
            # value is string with String variable reference
            (
                '#App:1234:my_ref!String',
                'string',
                'String with nested ref #App:1234:my_ref!String',
                'String with nested ref string',
            ),
            # value is string with StringArray reference
            (
                '#App:1234:my_ref!StringArray',
                ['string'],
                'String with nested ref #App:1234:my_ref!StringArray',
                'String with nested ref ["string"]',
            ),
            # value is string with KeyValue reference
            (
                '#App:1234:my_ref!KeyValue',
                {'key': 'key', 'value': 'value', 'type': 'any'},
                'String with nested ref #App:1234:my_ref!KeyValue',
                'String with nested ref {"key": "key", "value": "value", "type": "any"}',
            ),
            # value is string with KeyValueArray reference
            (
                '#App:1234:my_ref!KeyValueArray',
                [{'key': 'key', 'value': 'value', 'type': 'any'}],
                'String with nested ref #App:1234:my_ref!KeyValueArray',
                'String with nested ref [{"key": "key", "value": "value", "type": "any"}]',
            ),
            # value is string with TCEntity reference
            (
                '#App:1234:my_ref!TCEntity',
                {'id': '1', 'value': '1.1.1.1', 'type': 'Address'},
                'String with nested ref #App:1234:my_ref!TCEntity',
                'String with nested ref {"id": "1", "value": "1.1.1.1", "type": "Address"}',
            ),
            # value is string with TCEntityArray reference
            (
                '#App:1234:my_ref!TCEntityArray',
                [{'id': '1', 'value': '1.1.1.1', 'type': 'Address'}],
                'String with nested ref #App:1234:my_ref!TCEntityArray',
                'String with nested ref [{"id": "1", "value": "1.1.1.1", "type": "Address"}]',
            ),
            # value is string with reference that resolves to None
            # NOTE: need to be able to clear key value store between tests
            (
                '#App:1234:my_ref2!String',
                None,
                'String with nested ref #App:1234:my_ref2!String',
                'String with nested ref <null>',
            ),
            # value is string with reference to binary
            # need to add exception handling in read_embedded
            (
                '#App:1234:my_ref!Binary',
                b'binary string',
                'string with binary reference #App:1234:my_ref!Binary',
                'string with binary reference <binary>',
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
    ):
        """Test KeyValue field type with nested reference."""

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

        assert tcex.inputs.model.my_key_value == {  # type: ignore
            'key': 'my_key',
            'value': expected_value,
            'type': 'any',
        }

"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import KeyValueArray, KeyValueArrayOptional
from tcex.input.field_types.customizable import custom_key_value_array

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeKeyValueArray(InputTest):
    """Test TcEx KeyValueArray and KeyValueArrayOptional Inputs"""

    @pytest.mark.parametrize(
        'key_value,variable_name',
        [
            # KeyValue input
            # value is a String
            ({'key': 'username', 'value': 'test-user'}, '#App:1234:my_key_value!KeyValue'),
            # value is a StringArray
            ({'key': 'username', 'value': ['test-user']}, '#App:1234:my_key_value!KeyValue'),
            # value is Binary TODO: figure out how to pass binary data as 'value' for testing
            # ({'key': 'binary', 'value': '#App:1234:my_binary!Binary'},
            #  '#App:1234:my_key_value!KeyValue'),
            # value is Binary Array TODO: figure out how to pass binary data as 'value' for testing
            # (
            #     {'key': 'binary_array', 'value': '#App:1234:my_binary!BinaryArray'},
            #     '#App:1234:my_key_value!KeyValue',
            # ),
            # value is a TCEntity
            (
                {'key': 'entity', 'value': {'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}},
                '#App:1234:my_key_value!KeyValue',
            ),
            # value is a TCEntityArray
            (
                {'key': 'entity', 'value': [{'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}]},
                '#App:1234:my_key_value!KeyValue',
            ),
            # value is a KeyValue
            (
                {'key': 'nested', 'value': {'key': 'username', 'value': 'test-user'}},
                '#App:1234:my_key_value!KeyValue',
            ),
            # value is a KeyValue with optional variableType key
            (
                {
                    'key': 'nested',
                    'value': {'key': 'username', 'value': 'test-user', 'variableType': 'custom'},
                },
                '#App:1234:my_key_value!KeyValue',
            ),
            # value is a KeyValueArray
            (
                {'key': 'nested', 'value': [{'key': 'username', 'value': 'test-user'}]},
                '#App:1234:my_key_value!KeyValue',
            ),
            # KeyValueArray input
            # value is a String
            ([{'key': 'username', 'value': 'test-user'}], '#App:1234:my_key_value!KeyValueArray'),
            # value is a StringArray
            ([{'key': 'username', 'value': ['test-user']}], '#App:1234:my_key_value!KeyValueArray'),
            # value is Binary TODO: figure out how to pass binary data as 'value' for testing
            # ([{'key': 'binary', 'value': '#App:1234:my_binary!Binary'}],
            #  '#App:1234:my_key_value!KeyValueArray'),
            # value is Binary TODO: figure out how to pass binary array data as 'value' for testing
            # ([{'key': 'binary_array', 'value': '#App:1234:my_binary!BinaryArray'}],
            #  '#App:1234:my_key_value!KeyValueArray'),
            # value is a TCEntity
            (
                [{'key': 'entity', 'value': {'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}}],
                '#App:1234:my_key_value!KeyValueArray',
            ),
            # value is a TCEntityArray
            (
                [
                    {
                        'key': 'entity',
                        'value': [{'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}],
                    }
                ],
                '#App:1234:my_key_value!KeyValueArray',
            ),
            # value is a KeyValue
            (
                [{'key': 'nested', 'value': {'key': 'username', 'value': 'test-user'}}],
                '#App:1234:my_key_value!KeyValueArray',
            ),
            # value is a KeyValue with optional variableType key
            (
                {
                    'key': 'nested',
                    'value': [{'key': 'username', 'value': 'test-user', 'variableType': 'custom'}],
                },
                '#App:1234:my_key_value!KeyValue',
            ),
            # value is a KeyValueArray
            (
                [{'key': 'nested', 'value': [{'key': 'username', 'value': 'test-user'}]}],
                '#App:1234:my_key_value!KeyValueArray',
            ),
            # value is a KeyValueArray, KeyValueArray has a KeyValue with a nested KeyValue
            (
                # start of outermost KeyValueArray
                [
                    # first member of outermost KeyValueArray
                    {
                        'key': 'nested',
                        # 'value' is itself a KeyValueArray
                        'value': [
                            # KeyValue within KeyValueArray has a 'value' that is also a KeyValue
                            {'key': 'nested', 'value': {'key': 'username', 'value': 'test-user'}}
                        ],
                    }
                ],
                '#App:1234:my_key_value!KeyValueArray',
            ),
        ],
    )
    def test_field_type_key_value_array_input_kv_and_kv_array_staged(
        self, playbook_app: 'MockApp', key_value, variable_name
    ):
        """Test KeyValueArray field type with KeyValue and KeyValueArray input.

        Multiple variants tested (positive cases). Note that 'value' portion may be a String,
        StringArray, Binary, BinaryArray, TCEntity, TCEntityArray, KeyValue, KeyValueArray, or None.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
            key_value: A KeyValue or KeyValueArray
            variable_name: the variable to use to stage the key_value
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValueArray

        config_data = {'my_key_value': variable_name}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # stage Binary data into variable name set in KeyValue's value
        # if key_value['key'] == 'binary':
        #     self._stage_key_value('my_binary', key_value.get('value'), b'binary', tcex)
        # if key_value['key'] == 'binary_array':
        #     self._stage_key_value('my_binary', key_value.get('value'), [b'binary'], tcex)

        self._stage_key_value('my_key_value', variable_name, key_value, tcex)
        tcex.inputs.add_model(PytestModel)

        parsed_input = tcex.inputs.data.my_key_value

        # input will be wrapped in list if not already a list
        assert parsed_input == [key_value] if not isinstance(key_value, list) else key_value

    @staticmethod
    @pytest.mark.parametrize(
        'key_value',
        [
            # single KeyValue inputs
            # KeyValue missing 'key' field
            {'value': 'test-user'},
            # KeyValue missing 'value' field
            {'key': 'username'},
            # KeyValue has extra fields (therefore not a KeyValue)
            {'key': 'username', 'value': 'test-user', 'other': 'other'},
            # 'value' is a KeyValue that is missing 'key'
            {'key': 'username', 'value': {'value': 'test-user'}},
            # 'value' is a KeyValue that is missing 'value'
            {'key': 'username', 'value': {'key': 'username'}},
            # 'value' is a KeyValue that has extra fields (therefore not a KeyValue)
            {
                'key': 'username',
                'value': {'key': 'username', 'value': 'test-user', 'other': 'other'},
            },
            # 'value' is a KeyValueArray with KeyValue that is missing 'key'
            {'key': 'username', 'value': [{'value': 'test-user'}]},
            # 'value' is a KeyValueArray with KeyValue that is missing 'value'
            {'key': 'username', 'value': [{'key': 'username'}]},
            # 'value' is a KeyValueArray with KeyValue that has extra fields
            {
                'key': 'username',
                'value': [{'key': 'username', 'value': 'test-user', 'other': 'other'}],
            },
            # scenarios defined above, but with KeyValueArray inputs
            # KeyValue missing 'key' field
            [{'value': 'test-user'}],
            # KeyValue missing 'value' field
            [{'key': 'username'}],
            # KeyValue has extra fields (therefore not a KeyValue)
            [{'key': 'username', 'value': 'test-user', 'other': 'other'}],
            # 'value' is a KeyValue that is missing 'key'
            [{'key': 'username', 'value': {'value': 'test-user'}}],
            # 'value' is a KeyValue that is missing 'value'
            [{'key': 'username', 'value': {'key': 'username'}}],
            # 'value' is a KeyValue that has extra fields (therefore not a KeyValue)
            [
                {
                    'key': 'username',
                    'value': {'key': 'username', 'value': 'test-user', 'other': 'other'},
                }
            ],
            # 'value' is a KeyValueArray with KeyValue that is missing 'key'
            [{'key': 'username', 'value': [{'value': 'test-user'}]}],
            # 'value' is a KeyValueArray with KeyValue that is missing 'value'
            [{'key': 'username', 'value': [{'key': 'username'}]}],
            # 'value' is a KeyValueArray with KeyValue that has extra fields
            [
                {
                    'key': 'username',
                    'value': [{'key': 'username', 'value': 'test-user', 'other': 'other'}],
                }
            ],
        ],
    )
    def test_field_type_key_value_array_input_invalid(playbook_app: 'MockApp', key_value):
        """Test KeyValueArray field type with input that is considered invalid.

        Input value cannot be staged, as TCEX will not let use insert bad KeyValue data into
        KeyValue store.

        Args:
            playbook_app (fixture): An instance of MockApp.
            key_value: A KeyValue or KeyValueArray
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValueArray

        config_data = {'my_key_value': key_value}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert "is not of Array's type" in str(exc_info.value)

    @pytest.mark.parametrize(
        'key_value,variable_name',
        [
            # KeyValue input
            # value is an empty String
            ({'key': 'username', 'value': ''}, '#App:1234:my_key_value!KeyValue'),
            # value is empty Binary TODO: figure out how to pass binary data as 'value' for testing
            # ({'key': 'binary', 'value': '#App:1234:my_binary!Binary'},
            #  '#App:1234:my_key_value!KeyValue'),
            # value is an empty array
            (
                {'key': 'nested', 'value': []},
                '#App:1234:my_key_value!KeyValue',
            ),
        ],
    )
    def test_field_type_key_value_array_input_empty_key_value(
        self, playbook_app: 'MockApp', key_value, variable_name
    ):
        """Test KeyValueArray field type with KeyValue input that is considered empty. Error
        expected because emptiness checks are performed when KeyValueArray is initialized with
        an single KeyValue that is considered empty.

        see KeyValueArray.is_empty_member for information on what is considered an empty KeyValue.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
            key_value: A KeyValue or KeyValueArray
            variable_name: the variable to use to stage the key_value
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValueArray

        config_data = {'my_key_value': variable_name}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # stage Binary data into variable name set in KeyValue's value
        # if key_value['key'] == 'binary':
        #     self._stage_key_value('my_binary', key_value.get('value'), b'binary', tcex)
        # if key_value['key'] == 'binary_array':
        #     self._stage_key_value('my_binary', key_value.get('value'), [b'binary'], tcex)

        self._stage_key_value('my_key_value', variable_name, key_value, tcex)
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'may not be empty' in str(exc_info.value)

    @pytest.mark.parametrize(
        'key_value,variable_name',
        [
            # KeyValue input
            # value is an empty String
            ({'key': 'username', 'value': ''}, '#App:1234:my_key_value!KeyValue'),
            # value is an empty String
            ({'key': 'username', 'value': None}, '#App:1234:my_key_value!KeyValue'),
            # value is Binary TODO: figure out how to pass binary data as 'value' for testing
            # ({'key': 'binary', 'value': '#App:1234:my_binary!Binary'},
            #  '#App:1234:my_key_value!KeyValue'),
            # value is an empty array
            (
                {'key': 'nested', 'value': []},
                '#App:1234:my_key_value!KeyValue',
            ),
        ],
    )
    def test_field_type_key_value_array_optional_input_empty_key_value(
        self, playbook_app: 'MockApp', key_value, variable_name
    ):
        """Test KeyValueArrayOptional field type with KeyValue input that is considered empty.
        Empty KeyValues allowed through, as KeyValueArrayOptional type is used.

        See KeyValueArray.is_empty_member for information on what is considered an empty KeyValue.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
            key_value: A KeyValue or KeyValueArray
            variable_name: the variable to use to stage the key_value
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValueArrayOptional

        config_data = {'my_key_value': variable_name}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # stage Binary data into variable name set in KeyValue's value
        # if key_value['key'] == 'binary':
        #     self._stage_key_value('my_binary', key_value.get('value'), b'binary', tcex)
        # if key_value['key'] == 'binary_array':
        #     self._stage_key_value('my_binary', key_value.get('value'), [b'binary'], tcex)

        self._stage_key_value('my_key_value', variable_name, key_value, tcex)
        tcex.inputs.add_model(PytestModel)
        parsed_input = tcex.inputs.data.my_key_value
        assert parsed_input == [key_value] if not isinstance(key_value, list) else key_value

    @staticmethod
    def test_field_type_key_value_array_input_empty_array(playbook_app: 'MockApp'):
        """Test KeyValueArray field type with empty array input.

        This test is expected to fail, as KeyValueArrayOptional type is not used when
        defining my_key_value.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: Optional[KeyValueArray]

        config_data = {'my_key_value': []}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Array must have at least one element' in str(exc_info.value)

    @staticmethod
    def test_field_type_key_value_array_optional_input_empty_array(playbook_app: 'MockApp'):
        """Test KeyValueArrayOptional field type with empty array input.

        No Exception is expected, as KeyValueArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: Optional[KeyValueArrayOptional]

        config_data = {'my_key_value': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_key_value == []

    @staticmethod
    def test_field_type_key_value_array_input_null(playbook_app: 'MockApp'):
        """Test KeyValueArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValueArray

        config_data = {'my_key_value': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_key_value_array_optional_input_null(playbook_app: 'MockApp'):
        """Test KeyValueArrayOptional field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: KeyValueArrayOptional

        config_data = {'my_key_value': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_optional_field_type_key_value_array(playbook_app: 'MockApp'):
        """Test KeyValueArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of KeyValueArray with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: Optional[KeyValueArray]

        config_data = {'my_key_value': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_key_value is None

    @staticmethod
    def test_optional_field_type_key_value_array_optional(playbook_app: 'MockApp'):
        """Test KeyValueArrayOptional field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of KeyValueArrayOptional with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: Optional[KeyValueArrayOptional]

        config_data = {'my_key_value': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_key_value is None

    @staticmethod
    @pytest.mark.parametrize(
        'key_values',
        [
            # todo: need empty binary test after Bracey allows embedded binary support
            # None, keyvalue that is considered empty as it has empty value
            [
                None,
                {'key': 'username', 'value': ''},
            ],
            # None, keyvalue that is considered empty as it has empty list
            [
                None,
                {'key': 'username', 'value': []},
            ],
            # None, keyvalue that is considered null as it has None value
            [
                None,
                {'key': 'username', 'value': None},
            ],
        ],
    )
    def test_field_type_key_value_array_input_array_with_empty_and_null_members(
        playbook_app: 'MockApp', key_values
    ):
        """Test KeyValueArray field type with Array input that contains empty and null members.

        See KeyValueArray.is_empty_member and KeyValueArray.is_null_member for information on
        what is considered to be empty and null members of KeyValueArray.

        By default, KeyValueArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default, so no error expected.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_values: KeyValueArray

        config_data = {'my_key_values': key_values}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        # empty and null members are ok
        assert tcex.inputs.data.my_key_values == key_values

    @staticmethod
    @pytest.mark.parametrize(
        'key_values',
        [
            # todo: need empty binary test after Bracey allows embedded binary support
            # None, keyvalue that is considered empty as it has empty value
            [
                None,
                {'key': 'username', 'value': ''},
            ],
            [
                {'key': 'username', 'value': ''},
                None,
            ],
            # None, keyvalue that is considered empty as it has empty list
            [
                None,
                {'key': 'username', 'value': []},
            ],
            [
                {'key': 'username', 'value': []},
                None,
            ],
            # keyvalue that is considered empty as it has empty list,
            # keyvalue that is considered null as it has None value
            [
                {'key': 'username', 'value': []},
                {'key': 'username', 'value': None},
            ],
            [
                {'key': 'username', 'value': None},
                {'key': 'username', 'value': []},
            ],
            # keyvalue that is considered empty as it has empty string,
            # keyvalue that is considered null as it has None value
            [
                {'key': 'username', 'value': ''},
                {'key': 'username', 'value': None},
            ],
            [
                {'key': 'username', 'value': None},
                {'key': 'username', 'value': ''},
            ],
        ],
    )
    def test_field_type_key_value_array_input_array_with_empty_and_null_members_empty_not_allowed(
        playbook_app: 'MockApp', key_values
    ):
        """Test KeyValueArray field type with Array input that contains empty and null members.

        See KeyValueArray.is_empty_member and KeyValueArray.is_null_member for information on
        what is considered to be empty and null members of KeyValueArray.

        By default, KeyValueArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        KeyValueArray is configured to not accept empty members, so an error is expected due to
        empty members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_values: custom_key_value_array(allow_empty_members=False)

        config_data = {'my_key_values': key_values}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # assert None did not cause the issue
        assert 'None' not in err_msg
        # error due to empty members being in input
        assert 'may not be empty' in err_msg

    @staticmethod
    @pytest.mark.parametrize(
        'key_values',
        [
            # todo: need empty binary test after Bracey allows embedded binary support
            # None, keyvalue that is considered empty as it has empty value
            [
                None,
                {'key': 'username', 'value': ''},
            ],
            [
                {'key': 'username', 'value': ''},
                None,
            ],
            # None, keyvalue that is considered empty as it has empty list
            [
                None,
                {'key': 'username', 'value': []},
            ],
            [
                {'key': 'username', 'value': []},
                None,
            ],
            # keyvalue that is considered empty as it has empty list,
            # keyvalue that is considered null as it has None value
            [
                {'key': 'username', 'value': []},
                {'key': 'username', 'value': None},
            ],
            [
                {'key': 'username', 'value': None},
                {'key': 'username', 'value': []},
            ],
            # keyvalue that is considered empty as it has empty string,
            # keyvalue that is considered null as it has None value
            [
                {'key': 'username', 'value': ''},
                {'key': 'username', 'value': None},
            ],
            [
                {'key': 'username', 'value': None},
                {'key': 'username', 'value': ''},
            ],
        ],
    )
    def test_field_type_key_value_array_input_array_with_empty_and_null_members_null_not_allowed(
        playbook_app: 'MockApp', key_values
    ):
        """Test KeyValueArray field type with Array input that contains empty and/or null members.

        See KeyValueArray.is_empty_member and KeyValueArray.is_null_member for information on
        what is considered to be empty and null members of KeyValueArray.

        By default, KeyValueArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        KeyValueArray is configured to not accept null members, so an error is expected due to
        None or null members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_values: custom_key_value_array(allow_null_members=False)

        config_data = {'my_key_values': key_values}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # error due to None being in input
        assert 'None' in err_msg
        assert 'may not be null' in err_msg

    @staticmethod
    def test_custom_field_type_key_value_array_optional_keyword(playbook_app: 'MockApp'):
        """Test KeyValueArrayOptional field type with empty array input.

        This test simply asserts that passing optional=True to the custom Array factory function
        returns a custom Optional variant

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_key_value: Optional[custom_key_value_array(optional=True)]

        config_data = {'my_key_value': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert type(tcex.inputs.data.my_key_value).__name__ == 'KeyValueArrayOptionalCustom'

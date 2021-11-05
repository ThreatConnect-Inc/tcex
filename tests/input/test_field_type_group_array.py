"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import GroupArray, GroupArrayOptional
from tcex.input.field_types.customizable import custom_group_array
from tcex.input.field_types.exception import ConfigurationException

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeGroupArray(InputTest):
    """Test TcEx GroupArray and GroupArrayOptional Inputs"""

    def test_field_type_group_array_input_entity_staged(self, playbook_app: 'MockApp'):
        """Test GroupArray field type with TCEntity input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        entity = {'type': 'Adversary', 'value': 'Adversary Name', 'id': '1000'}
        config_data = {'my_group': '#App:1234:my_group!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_group', '#App:1234:my_group!TCEntity', entity, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group == [entity]

    def test_field_type_group_array_input_entity_array_staged(self, playbook_app: 'MockApp'):
        """Test GroupArray field type with TCEntity array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        entity = [{'type': 'Adversary', 'value': 'Adversary Name', 'id': '1000'}]
        config_data = {'my_group': '#App:1234:my_group!TCEntityArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_group', '#App:1234:my_group!TCEntityArray', entity, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group == entity

    def test_field_type_group_array_input_string_staged(self, playbook_app: 'MockApp'):
        """Test GroupArray field type with string input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        string = 'Adversary Name'
        config_data = {'my_group': '#App:1234:my_group!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_group', '#App:1234:my_group!String', string, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group == [string]

    def test_field_type_group_array_input_string_array_staged(self, playbook_app: 'MockApp'):
        """Test GroupArray field type with string array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        string = ['Adversary Name']
        config_data = {'my_group': '#App:1234:my_group!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_group', '#App:1234:my_group!StringArray', string, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group == string

    @pytest.mark.parametrize(
        'invalid_group',
        [
            # binary is not a valid Group type (not String and not TCEntity),
            b'not valid group',
            # has no value key
            {'type': 'Adversary', 'id': '100'},
            # has no type key
            {'value': 'Adversary Name', 'id': '100'},
            # type is empty string
            {'type': '', 'value': 'Adversary Name', 'id': '100'},
            # type is None
            {'type': None, 'value': 'Adversary Name', 'id': '100'},
            # type is not one of the valid Group types
            {'type': 'Address', 'value': '8.8.8.8', 'id': '100'},
            # type is anything else
            {'type': [], 'value': 'Adversary Name', 'id': '100'},
            # missing id
            {'type': 'Adversary', 'value': 'Adversary Name'},
            # id is blank
            {'type': 'Adversary', 'value': 'Adversary Name', 'id': ''},
            # id is None
            {'type': 'Adversary', 'value': 'Adversary Name', 'id': None},
            # value must be a string
            {'type': [], 'value': [], 'id': '100'},
            # same scenarios as above, except using array inputs
            [b'not valid group'],
            # has no value key
            [{'type': 'Adversary', 'id': '100'}],
            # has no type key
            [{'value': 'Adversary Name', 'id': '100'}],
            # type is empty string
            [{'type': '', 'value': 'Adversary Name', 'id': '100'}],
            # type is None
            [{'type': None, 'value': 'Adversary Name', 'id': '100'}],
            # type is not one of the valid Group types
            [{'type': 'Address', 'value': '8.8.8.8', 'id': '100'}],
            # type is anything else
            [{'type': [], 'value': 'Adversary Name', 'id': '100'}],
            # missing id
            [{'type': 'Adversary', 'value': 'Adversary Name'}],
            # id is blank
            [{'type': 'Adversary', 'value': 'Adversary Name', 'id': ''}],
            # id is None
            [{'type': 'Adversary', 'value': 'Adversary Name', 'id': None}],
            # value must be a string
            [{'type': [], 'value': [], 'id': '100'}],
        ],
    )
    def test_field_type_group_array_input_invalid(self, playbook_app: 'MockApp', invalid_group):
        """Test GroupArray field type with input that is neither String or TCEntity

        Exception expected, as values are not valid string or TCEntity values
        (multiple variants tested).
        This test validates both the passing of single invalid values and arrays of
        invalid values.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_item = invalid_group

        if isinstance(invalid_group, bytes):
            config_item = '#App:1234:my_group!Binary'

        if isinstance(invalid_group, list) and isinstance(invalid_group[0], bytes):
            config_item = '#App:1234:my_group!BinaryArray'

        config_data = {'my_group': config_item}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # must stage binary values
        if isinstance(invalid_group, bytes):
            self._stage_key_value('my_group', '#App:1234:my_group!Binary', invalid_group, tcex)

        if isinstance(invalid_group, list) and isinstance(invalid_group[0], bytes):
            self._stage_key_value('my_group', '#App:1234:my_group!BinaryArray', invalid_group, tcex)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert "not of Array's type" in err_msg

    @staticmethod
    def test_field_type_group_array_input_empty_array(playbook_app: 'MockApp'):
        """Test GroupArray field type with empty array input.

        This test is expected to fail, as GroupArrayOptional type is not used when
        defining my_group.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArray]

        config_data = {'my_group': []}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Array must have at least one element' in str(exc_info.value)

    @staticmethod
    def test_field_type_group_array_optional_input_empty_array(playbook_app: 'MockApp'):
        """Test GroupArrayOptional field type with empty array input.

        No Exception is expected, as GroupArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArrayOptional]

        config_data = {'my_group': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group == []

    def test_field_type_group_array_input_empty_entity(self, playbook_app: 'MockApp'):
        """Test GroupArray field type with empty input.

        Exception expected, as value is empty and GroupArrayOptional type is not used.

        Per TCEntityArray.is_empty_member, an empty entity is considered to be a
        dictionary that contains "type" and "value" keys and whose "value" key is an
        empty string. The "type" key must be a non-empty string in order for the
        value to be considered an Entity. As this Entity is a Group Entity, it must
        also have an "id".

        Args:
            playbook_app (fixture): An instance of MockApp.
        """
        group = {'type': 'Adversary', 'value': '', 'id': '1000'}

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArray]

        config_data = {'my_group': '#App:1234:my_group!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_group', '#App:1234:my_group!TCEntity', group, tcex)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        assert 'my_group' in err_msg
        assert 'may not be empty' in err_msg

    def test_field_type_group_array_optional_input_empty_entity(self, playbook_app: 'MockApp'):
        """Test GroupArrayOptional field type with empty input.

        No Exception is expected, as GroupArrayOptional type is used.

        Per TCEntityArray.is_empty_member, an empty entity is considered to be a
        dictionary that contains "type" and "value" keys and whose "value" key is an
        empty string. The "type" key must be a non-empty string in order for the
        value to be considered an Entity. As this Entity is a group Entity, it must
        also have an "id".

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        group = {'type': 'Adversary', 'value': '', 'id': '1000'}

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArrayOptional]

        config_data = {'my_group': '#App:1234:my_group!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_group', '#App:1234:my_group!TCEntity', group, tcex)
        tcex.inputs.add_model(PytestModel)

        # value coerced to Array (list)
        assert tcex.inputs.data.my_group == [group]

    @staticmethod
    def test_field_type_group_array_input_empty_string(playbook_app: 'MockApp'):
        """Test GroupArray field type with empty input.

        Exception expected, as value is empty and GroupArrayOptional type is not used.

        Plain strings are also valid GroupArray members. An empty string is considered
        an empty Group.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArray]

        config_data = {'my_group': ''}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        assert 'my_group' in err_msg
        assert 'may not be empty' in err_msg

    @staticmethod
    def test_field_type_group_array_optional_input_empty_string(playbook_app: 'MockApp'):
        """Test GroupArrayOptional field type with empty input.

        No Exception is expected, as GroupArrayOptional type is used.

        Plain strings are also valid GroupArray members. An empty string is considered
        an empty Group.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArrayOptional]

        config_data = {'my_group': ''}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        # value coerced to Array (list)
        assert tcex.inputs.data.my_group == ['']

    @staticmethod
    def test_field_type_group_array_input_null(playbook_app: 'MockApp'):
        """Test GroupArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray

        config_data = {'my_group': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_group_array_optional_input_null(playbook_app: 'MockApp'):
        """Test GroupArrayOptional field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArrayOptional

        config_data = {'my_group': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_optional_field_type_group_array(playbook_app: 'MockApp'):
        """Test GroupArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of GroupArray with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArray]

        config_data = {'my_group': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group is None

    @staticmethod
    def test_optional_field_type_group_array_optional(playbook_app: 'MockApp'):
        """Test GroupArrayOptional field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of GroupArrayOptional with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[GroupArrayOptional]

        config_data = {'my_group': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group is None

    @staticmethod
    def test_field_type_group_array_retrieval_methods(playbook_app: 'MockApp'):
        """Test 'entities' and 'values' methods inherited from IntelArray."""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group_array: GroupArray

        entity = {'type': 'Adversary', 'value': 'Adversary 2', 'id': '500'}
        ind_array = ['Adversary Name', entity]
        config_data = {'my_group_array': ind_array}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_group_array == ind_array

        # entities method returns only TCEntity members
        assert list(tcex.inputs.data.my_group_array.entities()) == [entity]

        # values method returns string members as well as 'value' key of TCEntity members
        assert list(tcex.inputs.data.my_group_array.values()) == ['Adversary Name', 'Adversary 2']

    @staticmethod
    @pytest.mark.parametrize(
        'groups',
        [
            # None, entity that is considered empty as it has empty value, and empty string
            [None, {'type': 'Adversary', 'value': '', 'id': '1000'}, ''],
            # None, entity that is considered null as it has None value, and empty string
            [None, {'type': 'Adversary', 'value': None, 'id': '1000'}, ''],
        ],
    )
    def test_field_type_group_array_input_array_with_empty_and_null_members(
        playbook_app: 'MockApp', groups
    ):
        """Test GroupArray field type with Array input that contains empty and null members.

        See GroupArray.is_empty_member and GroupArray.is_null_member for information on
        what is considered to be empty and null members of GroupArray.

        By default, GroupArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default, so no error expected.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_groups: GroupArray

        config_data = {'my_groups': groups}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        # empty and null members are ok
        assert tcex.inputs.data.my_groups == groups

    @staticmethod
    @pytest.mark.parametrize(
        'groups',
        [
            # None, and entity that is considered empty as it has empty value
            [None, {'type': 'Adversary', 'value': '', 'id': '1000'}],
            # same as above, but reverse order
            [{'type': 'Adversary', 'value': '', 'id': '1000'}, None],
            # entity that is considered null due to 'value' being None
            # and entity that is considered empty
            [
                {'type': 'Adversary', 'value': None, 'id': '1000'},
                {'type': 'Adversary', 'value': '', 'id': '1000'},
            ],
            [
                {'type': 'Adversary', 'value': '', 'id': '1000'},
                {'type': 'Adversary', 'value': None, 'id': '1000'},
            ],
            # entity that is considered null due to 'value' being None
            # and empty string
            [{'type': 'Adversary', 'value': None, 'id': '1000'}, ''],
            ['', {'type': 'Adversary', 'value': None, 'id': '1000'}],
            # None and empty string
            ['', None],
            [None, ''],
        ],
    )
    def test_field_type_group_array_input_array_with_empty_and_null_members_empty_not_allowed(
        playbook_app: 'MockApp', groups
    ):
        """Test GroupArray field type with Array input that contains empty and null members.

        See GroupArray.is_empty_member and GroupArray.is_null_member for information on
        what is considered to be empty and null members of GroupArray.

        By default, GroupArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        GroupArray is configured to not accept empty members, so an error is expected due to
        empty members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_groups: custom_group_array(allow_empty_members=False)

        config_data = {'my_groups': groups}
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
        'groups',
        [
            # None, and entity that is considered empty as it has empty value
            [None, {'type': 'Adversary', 'value': '', 'id': '1000'}],
            # same as above, but reverse order
            [{'type': 'Adversary', 'value': '', 'id': '1000'}, None],
            # entity that is considered null due to 'value' being None
            # and entity that is considered empty
            [
                {'type': 'Adversary', 'value': None, 'id': '1000'},
                {'type': 'Adversary', 'value': '', 'id': '1000'},
            ],
            [
                {'type': 'Adversary', 'value': '', 'id': '1000'},
                {'type': 'Adversary', 'value': None, 'id': '1000'},
            ],
            # entity that is considered null due to 'value' being None
            # and empty string
            [{'type': 'Adversary', 'value': None, 'id': '1000'}, ''],
            ['', {'type': 'Adversary', 'value': None, 'id': '1000'}],
            # None and empty string
            ['', None],
            [None, ''],
        ],
    )
    def test_field_type_group_array_input_array_with_empty_and_null_members_null_not_allowed(
        playbook_app: 'MockApp', groups
    ):
        """Test GroupArray field type with Array input that contains empty and/or null members.

        See GroupArray.is_empty_member and GroupArray.is_null_member for information on
        what is considered to be empty and null members of GroupArray.

        By default, GroupArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        GroupArray is configured to not accept null members, so an error is expected due to
        None or null members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_groups: custom_group_array(allow_null_members=False)

        config_data = {'my_groups': groups}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # error due to None being in input
        assert 'None' in err_msg
        assert 'may not be null' in err_msg

    @staticmethod
    @pytest.mark.parametrize(
        'types',
        [
            # contains indicator
            ['Address'],
            # contains random string
            ['other'],
            # contains something other than string
            [{}],
            # contains None
            [None],
            # is not a list
            {},
        ],
    )
    def test_field_type_group_array_custom_entity_filters_invalid(playbook_app: 'MockApp', types):
        """Test the entity_filter_types customization option of custom_group_array.

        The parameter should not allow anything that is not a list of valid group types.
        """
        # ensure session singleton is loaded
        app = playbook_app(config_data={})
        tcex = app.tcex
        _ = tcex.session_tc

        # should raise exception on custom group array config
        with pytest.raises(ConfigurationException):
            custom_group_array(entity_filter_types=types)

    @staticmethod
    @pytest.mark.parametrize('types', [['Adversary'], ['Campaign'], ['Adversary', 'Campaign']])
    def test_field_type_group_array_custom_entity_filters_valid(playbook_app: 'MockApp', types):
        """Test the entity_filter_types customization option of custom_group_array.

        The parameter should not allow anything that is not a list of valid group types.
        """
        groups = [
            {'type': 'Adversary', 'value': 'Adversary Name', 'id': '1000'},
            {'type': 'Campaign', 'value': 'Test Campaign', 'id': '1000'},
        ]

        config_data = {'my_groups': groups}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # ensure session singleton is loaded
        _ = tcex.session_tc

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_groups: custom_group_array(entity_filter_types=types)

        tcex.inputs.add_model(PytestModel)
        entities = list(tcex.inputs.data.my_groups.entities())

        # should only contain entities with type that is in configured filter types
        assert all(entity['type'] in types for entity in entities)

    @staticmethod
    def test_custom_field_type_group_array_with_optional_keyword(playbook_app: 'MockApp'):
        """Test custom GroupArrayOptional field type

        This test simply asserts that passing optional=True to the custom Array factory function
        returns a custom Optional variant

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        config_data = {'my_group': ''}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # ensure session singleton is loaded
        _ = tcex.session_tc

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: Optional[custom_group_array(optional=True)]

        tcex.inputs.add_model(PytestModel)

        assert type(tcex.inputs.data.my_group).__name__ == 'GroupArrayOptionalCustom'

"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import GroupArray, GroupArrayOptional

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

    def test_field_type_group_array_input_invalid(self, playbook_app: 'MockApp'):
        """Test GroupArray field type with input that is neither String or TCEntity

        Exception expected, as values are not valid string or TCEntity values
        (multiple variants tested).
        This test validates both the passing of single invalid values and arrays of
        invalid values.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        # binary is not a valid Group type (not String and not TCEntity)
        invalid_group = b'not valid group'
        # has no value key
        invalid_group2 = {'type': 'Adversary', 'id': '100'}
        # has no type key
        invalid_group3 = {'value': 'Adversary Name', 'id': '100'}
        # type is empty string
        invalid_group4 = {'type': '', 'value': 'Adversary Name', 'id': '100'}
        # type is None
        invalid_group5 = {'type': None, 'value': 'Adversary Name', 'id': '100'}
        # type is not one of the valid Group types
        invalid_group6 = {'type': 'Address', 'value': '8.8.8.8', 'id': '100'}
        # type is anything else
        invalid_group7 = {'type': [], 'value': 'Adversary Name', 'id': '100'}
        # missing id
        invalid_group8 = {'type': 'Adversary', 'value': 'Adversary Name'}
        # id is blank
        invalid_group9 = {'type': 'Adversary', 'value': 'Adversary Name', 'id': ''}
        # id is None
        invalid_group10 = {'type': 'Adversary', 'value': 'Adversary Name', 'id': None}
        # value must be a string
        invalid_group11 = {'type': [], 'value': [], 'id': '100'}

        # same scenarios as above, except using array inputs
        invalid_group12 = [b'not valid group']
        # has no value key
        invalid_group13 = [{'type': 'Adversary', 'id': '100'}]
        # has no type key
        invalid_group14 = [{'value': 'Adversary Name', 'id': '100'}]
        # type is empty string
        invalid_group15 = [{'type': '', 'value': 'Adversary Name', 'id': '100'}]
        # type is None
        invalid_group16 = [{'type': None, 'value': 'Adversary Name', 'id': '100'}]
        # type is not one of the valid Group types
        invalid_group17 = [{'type': 'Address', 'value': '8.8.8.8', 'id': '100'}]
        # type is anything else
        invalid_group18 = [{'type': [], 'value': 'Adversary Name', 'id': '100'}]
        # missing id
        invalid_group19 = [{'type': 'Adversary', 'value': 'Adversary Name'}]
        # id is blank
        invalid_group20 = [{'type': 'Adversary', 'value': 'Adversary Name', 'id': ''}]
        # id is None
        invalid_group21 = [{'type': 'Adversary', 'value': 'Adversary Name', 'id': None}]
        # value must be a string
        invalid_group22 = [{'type': [], 'value': [], 'id': '100'}]

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_group: GroupArray
            my_group2: GroupArray
            my_group3: GroupArray
            my_group4: GroupArray
            my_group5: GroupArray
            my_group6: GroupArray
            my_group7: GroupArray
            my_group8: GroupArray
            my_group9: GroupArray
            my_group10: GroupArray
            my_group11: GroupArray
            my_group12: GroupArray
            my_group13: GroupArray
            my_group14: GroupArray
            my_group15: GroupArray
            my_group16: GroupArray
            my_group17: GroupArray
            my_group18: GroupArray
            my_group19: GroupArray
            my_group20: GroupArray
            my_group21: GroupArray
            my_group22: GroupArray

        config_data = {
            'my_group': '#App:1234:my_group!Binary',
            'my_group2': invalid_group2,
            'my_group3': invalid_group3,
            'my_group4': invalid_group4,
            'my_group5': invalid_group5,
            'my_group6': invalid_group6,
            'my_group7': invalid_group7,
            'my_group8': invalid_group8,
            'my_group9': invalid_group9,
            'my_group10': invalid_group10,
            'my_group11': invalid_group11,
            'my_group12': '#App:1234:my_group12!Binary',
            'my_group13': invalid_group13,
            'my_group14': invalid_group14,
            'my_group15': invalid_group15,
            'my_group16': invalid_group16,
            'my_group17': invalid_group17,
            'my_group18': invalid_group18,
            'my_group19': invalid_group19,
            'my_group20': invalid_group20,
            'my_group21': invalid_group21,
            'my_group22': invalid_group22,
        }
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # must stage binary values
        self._stage_key_value('my_group', '#App:1234:my_group!Binary', invalid_group, tcex)
        self._stage_key_value(
            'my_group12', '#App:1234:my_group12!BinaryArray', invalid_group12, tcex
        )

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # all GroupArray definitions in model resulted in error
        assert all(entity in err_msg for entity in config_data.keys())

        # all GroupArray definitions resulted in the same error
        assert err_msg.count("not of Array's type") == len(config_data.keys())

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

    def test_field_type_group_array_input_empty_string(self, playbook_app: 'MockApp'):
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

    def test_field_type_group_array_optional_input_empty_string(self, playbook_app: 'MockApp'):
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

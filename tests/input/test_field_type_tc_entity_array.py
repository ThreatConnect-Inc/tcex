"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import TCEntityArray, TCEntityArrayOptional
from tcex.input.field_types.customizable import custom_tc_entity_array

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeTCEntityArray(InputTest):
    """Test TcEx TCEntityArray and TCEntityArrayOptional Inputs"""

    def test_field_type_entity_array_input_entity_staged(self, playbook_app: 'MockApp'):
        """Test TCEntityArray field type with TCEntity input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: TCEntityArray

        entity = {'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}
        config_data = {'my_entity': '#App:1234:my_entity!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_entity', '#App:1234:my_entity!TCEntity', entity, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_entity == [entity]

    def test_field_type_entity_array_input_entity_array_staged(self, playbook_app: 'MockApp'):
        """Test TCEntityArray field type with TCEntity array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: TCEntityArray

        entity = [{'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}]
        config_data = {'my_entity': '#App:1234:my_entity!TCEntityArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_entity', '#App:1234:my_entity!TCEntityArray', entity, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_entity == entity

    @pytest.mark.parametrize(
        'invalid_entity',
        [
            'not a tc entity',
            # has no value key
            {'type': 'Address', 'id': '10001'},
            # has no type key
            {'value': '8.8.8.8', 'id': '10001'},
            # type is empty string
            {'type': '', 'value': '8.8.8.8', 'id': '10001'},
            # type is None
            {'type': None, 'value': '8.8.8.8', 'id': '10001'},
            # type is anything else
            {'type': [], 'value': '8.8.8.8', 'id': '10001'},
            # value is not a string (check covers, indicators, groups, etc.),
            {'type': 'Address', 'value': [], 'id': '10001'},
            # Indicator has no id
            {'type': 'Address', 'value': '8.8.8.8'},
            # Indicator id is not string
            {'type': 'Address', 'value': '8.8.8.8', 'id': []},
            # Group has no id
            {'type': 'Adversary', 'value': 'Adversary Name'},
            # Group id is not string
            {'type': 'Adversary', 'value': 'Adversary Name', 'id': []},
            # has extra keys
            {'type': 'Adversary', 'value': 'Adversary Name', 'id': '1001', 'other': 'another'},
            # same scenarios as above, except using array inputs
            ['not a tc entity'],
            # has no value key
            [{'type': 'Address', 'id': '10001'}],
            # has no type key
            [{'value': '8.8.8.8', 'id': '10001'}],
            # type is empty string
            [{'type': '', 'value': '8.8.8.8', 'id': '10001'}],
            # type is None
            [{'type': None, 'value': '8.8.8.8', 'id': '10001'}],
            # type is anything else
            [{'type': [], 'value': '8.8.8.8', 'id': '10001'}],
            # value is not a string (check covers, indicators, groups, etc.),
            [{'type': 'Address', 'value': [], 'id': '10001'}],
            # Indicator has no id
            [{'type': 'Address', 'value': '8.8.8.8'}],
            # Indicator id is not string
            [{'type': 'Address', 'value': '8.8.8.8', 'id': []}],
            # Group has no id
            [{'type': 'Adversary', 'value': 'Adversary Name'}],
            # Group id is not string
            [{'type': 'Adversary', 'value': 'Adversary Name', 'id': []}],
            # has extra keys
            [{'type': 'Adversary', 'value': 'Adversary Name', 'id': '1001', 'other': 'another'}],
        ],
    )
    def test_field_type_entity_array_input_invalid(self, playbook_app: 'MockApp', invalid_entity):
        """Test TCEntityArray field type with non-TCEntity input.

        Exception expected, as values are not TCEntity values (multiple variants tested).
        This test validates both the passing of single invalid values and arrays of
        invalid values.

        Per TCEntityArray.is_array_member, a TCEntity (array member) must be a dictionary that
        contains "type" and "value" keys. The "type" key must be a non-empty string.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: TCEntityArray

        config_data = {
            'my_entity': invalid_entity,
        }
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert "not of Array's type" in str(exc_info.value)

    @staticmethod
    def test_field_type_entity_array_input_empty_array(playbook_app: 'MockApp'):
        """Test TCEntityArray field type with empty array input.

        This test is expected to fail, as TCEntityArrayOptional type is not used when
        defining my_entity.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: Optional[TCEntityArray]

        config_data = {'my_entity': []}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Array must have at least one element' in str(exc_info.value)

    @staticmethod
    def test_field_type_entity_array_optional_input_empty_array(playbook_app: 'MockApp'):
        """Test TCEntityArray field type with empty array input.

        No Exception is expected, as TCEntityArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: Optional[TCEntityArrayOptional]

        config_data = {'my_entity': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_entity == []

    def test_field_type_entity_array_input_empty_entity(self, playbook_app: 'MockApp'):
        """Test TCEntityArray field type with empty input.

        Exception expected, as value is empty and TCEntityArrayOptional type is not used.

        Per TCEntityArray.is_empty_member, an empty entity is considered to be a
        dictionary that contains "type" and "value" keys and whose "value" key is an
        empty string. The "type" key must be a non-empty string in order for the
        value to be considered an Entity.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """
        entity = {'type': 'Address', 'value': '', 'id': '1000'}

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # test for both empty cases
            my_entity: Optional[TCEntityArray]

        config_data = {'my_entity': '#App:1234:my_entity!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_entity', '#App:1234:my_entity!TCEntity', entity, tcex)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        assert 'my_entity' in err_msg
        assert 'may not be empty' in err_msg

    def test_field_type_entity_array_optional_input_empty_entity(self, playbook_app: 'MockApp'):
        """Test TCEntityArray field type with empty input.

        No Exception is expected, as TCEntityArrayOptional type is used.

        Per TCEntityArray.is_empty_member, an empty entity is considered to be a
        dictionary that contains "type" and "value" keys and whose "value" key is an
        empty string. The "type" key must be a non-empty string in order for the
        value to be considered an Entity.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        entity = {'type': 'File', 'value': '', 'id': '1000'}

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            # test for both empty cases
            my_entity: Optional[TCEntityArrayOptional]

        config_data = {
            'my_entity': '#App:1234:my_entity!TCEntity',
        }
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_entity', '#App:1234:my_entity!TCEntity', entity, tcex)
        tcex.inputs.add_model(PytestModel)

        # values coerced to Arrays (list)
        assert tcex.inputs.data.my_entity == [entity]

    @staticmethod
    def test_field_type_entity_array_input_null(playbook_app: 'MockApp'):
        """Test TCEntityArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: TCEntityArray

        config_data = {'my_entity': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_entity_array_optional_input_null(playbook_app: 'MockApp'):
        """Test TCEntityArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: TCEntityArrayOptional

        config_data = {'my_entity': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_optional_field_type_entity_array(playbook_app: 'MockApp'):
        """Test TCEntityArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of TCEntityArray with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: Optional[TCEntityArray]

        config_data = {'my_entity': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_entity is None

    @staticmethod
    def test_optional_field_type_entity_array_optional(playbook_app: 'MockApp'):
        """Test TCEntityArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of TCEntityArrayOptional with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: Optional[TCEntityArrayOptional]

        config_data = {'my_entity': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_entity is None

    @pytest.mark.parametrize(
        'entity',
        [
            # None, and entity that is considered empty as it has empty value
            [None, {'type': 'Address', 'value': '', 'id': '1000'}],
            # None, and entity that is considered empty as it has None value
            [None, {'type': 'Address', 'value': None, 'id': '1000'}],
        ],
    )
    def test_field_type_tc_entity_array_input_array_with_empty_and_null_members(
        self, playbook_app: 'MockApp', entity
    ):
        """Test TCEntityArray field type with Array input that contains empty and null members.

        See TCEntityArray.is_empty_member and TCEntityArray.is_null_member for information on
        what is considered to be empty and null members of TCEntityArray.

        By default, TCEntityArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default, so no error expected.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: TCEntityArray

        config_data = {'my_entity': entity}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        # empty and null members are ok
        assert tcex.inputs.data.my_entity == entity

    @pytest.mark.parametrize(
        'entity',
        [
            # entity that is considered empty as it has empty value
            [{'type': 'Address', 'value': '', 'id': '1000'}],
            # None, and entity that is considered empty as it has empty value
            [None, {'type': 'Address', 'value': '', 'id': '1000'}],
            # same as above, but in reverse order
            [{'type': 'Address', 'value': '', 'id': '1000'}, None],
        ],
    )
    def test_field_type_tc_entity_array_input_array_with_empty_and_null_members_empty_not_allowed(
        self, playbook_app: 'MockApp', entity
    ):
        """Test TCEntityArray field type with Array input that contains empty and null members.

        See TCEntityArray.is_empty_member and TCEntityArray.is_null_member for information on
        what is considered to be empty and null members of TCEntityArray.

        By default, TCEntityArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        TCEntityArray is configured to not accept empty members, so an error is expected due to
        empty members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: custom_tc_entity_array(allow_empty_members=False)

        config_data = {'my_entity': entity}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        # error due to b'' being in input
        assert 'may not be empty' in str(exc_info.value)

    @pytest.mark.parametrize(
        'entity',
        [
            # null entity
            [None],
            # None, and entity that is considered empty as it has empty value
            [None, {'type': 'Address', 'value': '', 'id': '1000'}],
            # same as above, but reverse order
            [{'type': 'Address', 'value': '', 'id': '1000'}, None],
            # entity that is considered null due to 'value' being None
            [{'type': 'Address', 'value': None, 'id': '1000'}],
        ],
    )
    def test_field_type_tc_entity_array_input_array_with_empty_and_null_members_null_not_allowed(
        self, playbook_app: 'MockApp', entity
    ):
        """Test TCEntityArray field type with Array input that contains empty and/or null members.

        See TCEntityArray.is_empty_member and TCEntityArray.is_null_member for information on
        what is considered to be empty and null members of TCEntityArray.

        By default, TCEntityArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        TCEntityArray is configured to not accept null members, so an error is expected due to
        None or null members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_entity: custom_tc_entity_array(allow_null_members=False)

        config_data = {'my_entity': entity}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        # error due to None being in input
        assert 'may not be null' in str(exc_info.value)

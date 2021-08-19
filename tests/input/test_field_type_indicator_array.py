"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import IndicatorArray, IndicatorArrayOptional
from tcex.input.field_types.customizable import custom_indicator_array
from tcex.input.field_types.exception import ConfigurationException

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeIndicatorArray(InputTest):
    """Test TcEx IndicatorArray and IndicatorArrayOptional Inputs"""

    def test_field_type_indicator_array_input_entity_staged(self, playbook_app: 'MockApp'):
        """Test IndicatorArray field type with TCEntity input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        entity = {'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}
        config_data = {'my_indicator': '#App:1234:my_indicator!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_indicator', '#App:1234:my_indicator!TCEntity', entity, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator == [entity]

    def test_field_type_indicator_array_input_entity_array_staged(self, playbook_app: 'MockApp'):
        """Test IndicatorArray field type with TCEntity array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        entity = [{'type': 'Address', 'value': '8.8.8.8', 'id': '1000'}]
        config_data = {'my_indicator': '#App:1234:my_indicator!TCEntityArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_indicator', '#App:1234:my_indicator!TCEntityArray', entity, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator == entity

    def test_field_type_indicator_array_input_string_staged(self, playbook_app: 'MockApp'):
        """Test IndicatorArray field type with string input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        string = '8.8.8.8'
        config_data = {'my_indicator': '#App:1234:my_indicator!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_indicator', '#App:1234:my_indicator!String', string, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator == [string]

    def test_field_type_indicator_array_input_string_array_staged(self, playbook_app: 'MockApp'):
        """Test IndicatorArray field type with string array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        string = ['8.8.8.8']
        config_data = {'my_indicator': '#App:1234:my_indicator!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_indicator', '#App:1234:my_indicator!StringArray', string, tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator == string

    @pytest.mark.parametrize(
        'invalid_indicator',
        [
            # binary is not a valid indicator type (not String and not TCEntity),
            b'not valid indicator',
            # has no value key
            {'type': 'Address', 'id': '100'},
            # has no type key
            {'value': '8.8.8.8', 'id': '100'},
            # type is empty string
            {'type': '', 'value': '8.8.8.8', 'id': '100'},
            # type is None
            {'type': None, 'value': '8.8.8.8', 'id': '100'},
            # type is not one of the valid indicator types
            {'type': 'Adversary', 'value': 'Adversary Name', 'id': '100'},
            # type is anything else
            {'type': [], 'value': '8.8.8.8', 'id': '100'},
            # missing id
            {'type': 'Address', 'value': '8.8.8.8'},
            # id is blank
            {'type': 'Address', 'value': '8.8.8.8', 'id': ''},
            # id is None
            {'type': 'Address', 'value': '8.8.8.8', 'id': None},
            # value must be a string
            {'type': [], 'value': [], 'id': '100'},
            # same scenarios as above, except using array inputs
            [b'not valid indicator'],
            # has no value key
            [{'type': 'Address', 'id': '100'}],
            # has no type key
            [{'value': '8.8.8.8', 'id': '100'}],
            # type is empty string
            [{'type': '', 'value': '8.8.8.8', 'id': '100'}],
            # type is None
            [{'type': None, 'value': '8.8.8.8', 'id': '100'}],
            # type is not one of the valid indicator types
            [{'type': 'Adversary', 'value': 'Adversary Name', 'id': '100'}],
            # type is anything else
            [{'type': [], 'value': '8.8.8.8', 'id': '100'}],
            # missing id
            [{'type': 'Address', 'value': '8.8.8.8'}],
            # id is blank
            [{'type': 'Address', 'value': '8.8.8.8', 'id': ''}],
            # id is None
            [{'type': 'Address', 'value': '8.8.8.8', 'id': None}],
            # value must be a string
            [{'type': [], 'value': [], 'id': '100'}],
        ],
    )
    def test_field_type_indicator_array_input_invalid(
        self, playbook_app: 'MockApp', invalid_indicator
    ):
        """Test IndicatorArray field type with input that is neither String or TCEntity

        Exception expected, as values are not valid string or TCEntity values
        (multiple variants tested).
        This test validates both the passing of single invalid values and arrays of
        invalid values.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_item = invalid_indicator

        if isinstance(invalid_indicator, bytes):
            config_item = '#App:1234:my_indicator!Binary'

        if isinstance(invalid_indicator, list) and isinstance(invalid_indicator[0], bytes):
            config_item = '#App:1234:my_indicator!BinaryArray'

        config_data = {'my_indicator': config_item}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # must stage binary values
        if isinstance(invalid_indicator, bytes):
            self._stage_key_value(
                'my_indicator', '#App:1234:my_indicator!Binary', invalid_indicator, tcex
            )

        if isinstance(invalid_indicator, list) and isinstance(invalid_indicator[0], bytes):
            self._stage_key_value(
                'my_indicator', '#App:1234:my_indicator!BinaryArray', invalid_indicator, tcex
            )

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert "not of Array's type" in err_msg

    @staticmethod
    def test_field_type_indicator_array_input_empty_array(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with empty array input.

        This test is expected to fail, as IndicatorArrayOptional type is not used when
        defining my_indicator.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArray]

        config_data = {'my_indicator': []}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Array must have at least one element' in str(exc_info.value)

    @staticmethod
    def test_field_type_indicator_array_optional_input_empty_array(playbook_app: 'MockApp'):
        """Test IndicatorArrayOptional field type with empty array input.

        No Exception is expected, as IndicatorArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArrayOptional]

        config_data = {'my_indicator': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator == []

    def test_field_type_indicator_array_input_empty_entity(self, playbook_app: 'MockApp'):
        """Test IndicatorArray field type with empty input.

        Exception expected, as value is empty and IndicatorArrayOptional type is not used.

        Per TCEntityArray.is_empty_member, an empty entity is considered to be a
        dictionary that contains "type" and "value" keys and whose "value" key is an
        empty string. The "type" key must be a non-empty string in order for the
        value to be considered an Entity. As this Entity is an Indicator Entity, it must
        also have an "id".

        Args:
            playbook_app (fixture): An instance of MockApp.
        """
        indicator = {'type': 'Address', 'value': '', 'id': '1000'}

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArray]

        config_data = {'my_indicator': '#App:1234:my_indicator!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_indicator', '#App:1234:my_indicator!TCEntity', indicator, tcex)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        assert 'my_indicator' in err_msg
        assert 'may not be empty' in err_msg

    def test_field_type_indicator_array_optional_input_empty_entity(self, playbook_app: 'MockApp'):
        """Test IndicatorArrayOptional field type with empty input.

        No Exception is expected, as IndicatorArrayOptional type is used.

        Per TCEntityArray.is_empty_member, an empty entity is considered to be a
        dictionary that contains "type" and "value" keys and whose "value" key is an
        empty string. The "type" key must be a non-empty string in order for the
        value to be considered an Entity. As this Entity is an Indicator Entity, it must
        also have an "id".

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        indicator = {'type': 'File', 'value': '', 'id': '1000'}

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArrayOptional]

        config_data = {'my_indicator': '#App:1234:my_indicator!TCEntity'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_indicator', '#App:1234:my_indicator!TCEntity', indicator, tcex)
        tcex.inputs.add_model(PytestModel)

        # value coerced to Array (list)
        assert tcex.inputs.data.my_indicator == [indicator]

    def test_field_type_indicator_array_input_empty_string(self, playbook_app: 'MockApp'):
        """Test IndicatorArray field type with empty input.

        Exception expected, as value is empty and IndicatorArrayOptional type is not used.

        Plain strings are also valid IndicatorArray members. An empty string is considered
        an empty Indicator.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArray]

        config_data = {'my_indicator': ''}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        assert 'my_indicator' in err_msg
        assert 'may not be empty' in err_msg

    def test_field_type_indicator_array_optional_input_empty_string(self, playbook_app: 'MockApp'):
        """Test IndicatorArrayOptional field type with empty input.

        No Exception is expected, as IndicatorArrayOptional type is used.

        Plain strings are also valid IndicatorArray members. An empty string is considered
        an empty Indicator.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArrayOptional]

        config_data = {'my_indicator': ''}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        # value coerced to Array (list)
        assert tcex.inputs.data.my_indicator == ['']

    @staticmethod
    def test_field_type_indicator_array_input_null(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray

        config_data = {'my_indicator': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_indicator_array_optional_input_null(playbook_app: 'MockApp'):
        """Test IndicatorArrayOptional field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArrayOptional

        config_data = {'my_indicator': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_optional_field_type_indicator_array(playbook_app: 'MockApp'):
        """Test IndicatorArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of IndicatorArray with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArray]

        config_data = {'my_indicator': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator is None

    @staticmethod
    def test_optional_field_type_indicator_array_optional(playbook_app: 'MockApp'):
        """Test IndicatorArrayOptional field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of IndicatorArrayOptional with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: Optional[IndicatorArrayOptional]

        config_data = {'my_indicator': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator is None

    @staticmethod
    def test_field_type_indicator_array_retrieval_methods(playbook_app: 'MockApp'):
        """Test 'entities' and 'values' methods inherited from IntelArray."""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator_array: IndicatorArray

        entity = {'type': 'Address', 'value': '1.1.1.1', 'id': '500'}
        ind_array = ['8.8.8.8', entity]
        config_data = {'my_indicator_array': ind_array}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_indicator_array == ind_array

        # entities method returns only TCEntity members
        assert list(tcex.inputs.data.my_indicator_array.entities()) == [entity]

        # values method returns string members as well as 'value' key of TCEntity members
        assert list(tcex.inputs.data.my_indicator_array.values()) == ['8.8.8.8', '1.1.1.1']

    @pytest.mark.parametrize(
        'indicators',
        [
            # None, entity that is considered empty as it has empty value, and empty string
            [None, {'type': 'Address', 'value': '', 'id': '1000'}, ''],
            # None, entity that is considered null as it has None value, and empty string
            [None, {'type': 'Address', 'value': None, 'id': '1000'}, ''],
        ],
    )
    def test_field_type_indicator_array_input_array_with_empty_and_null_members(
        self, playbook_app: 'MockApp', indicators
    ):
        """Test IndicatorArray field type with Array input that contains empty and null members.

        See IndicatorArray.is_empty_member and IndicatorArray.is_null_member for information on
        what is considered to be empty and null members of IndicatorArray.

        By default, IndicatorArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default, so no error expected.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicators: IndicatorArray

        config_data = {'my_indicators': indicators}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        tcex.inputs.add_model(PytestModel)

        # empty and null members are ok
        assert tcex.inputs.data.my_indicators == indicators

    @pytest.mark.parametrize(
        'indicators',
        [
            # None, and entity that is considered empty as it has empty value
            [None, {'type': 'Address', 'value': '', 'id': '1000'}],
            # same as above, but in reverse order
            [{'type': 'Address', 'value': '', 'id': '1000'}, None],
            # entity that is considered null an entity that is considered empty
            [
                {'type': 'Address', 'value': None, 'id': '1000'},
                {'type': 'Address', 'value': '', 'id': '1000'},
            ],
            [
                {'type': 'Address', 'value': '', 'id': '1000'},
                {'type': 'Address', 'value': None, 'id': '1000'},
            ],
            # entity that is considered null and empty string
            [{'type': 'Address', 'value': None, 'id': '1000'}, ''],
            ['', {'type': 'Address', 'value': None, 'id': '1000'}],
            # None and empty string
            [None, ''],
            ['', None],
        ],
    )
    def test_field_type_indicator_array_input_array_with_empty_and_null_members_empty_not_allowed(
        self, playbook_app: 'MockApp', indicators
    ):
        """Test IndicatorArray field type with Array input that contains empty and null members.

        See IndicatorArray.is_empty_member and IndicatorArray.is_null_member for information on
        what is considered to be empty and null members of IndicatorArray.

        By default, IndicatorArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        IndicatorArray is configured to not accept empty members, so an error is expected due to
        empty members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicators: custom_indicator_array(allow_empty_members=False)

        config_data = {'my_indicators': indicators}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # assert None did not cause the issue
        assert 'None' not in err_msg
        # error due to empty members being in input
        assert 'may not be empty' in err_msg

    @pytest.mark.parametrize(
        'indicators',
        [
            # None, and entity that is considered empty as it has empty value
            [None, {'type': 'Address', 'value': '', 'id': '1000'}],
            # same as above, but in reverse order
            [{'type': 'Address', 'value': '', 'id': '1000'}, None],
            # entity that is considered null an entity that is considered empty
            [
                {'type': 'Address', 'value': None, 'id': '1000'},
                {'type': 'Address', 'value': '', 'id': '1000'},
            ],
            [
                {'type': 'Address', 'value': '', 'id': '1000'},
                {'type': 'Address', 'value': None, 'id': '1000'},
            ],
            # entity that is considered null and empty string
            [{'type': 'Address', 'value': None, 'id': '1000'}, ''],
            ['', {'type': 'Address', 'value': None, 'id': '1000'}],
            # None and empty string
            [None, ''],
            ['', None],
        ],
    )
    def test_field_type_indicator_array_input_array_with_empty_and_null_members_null_not_allowed(
        self, playbook_app: 'MockApp', indicators
    ):
        """Test IndicatorArray field type with Array input that contains empty and/or null members.

        See IndicatorArray.is_empty_member and IndicatorArray.is_null_member for information on
        what is considered to be empty and null members of IndicatorArray.

        By default, IndicatorArray only checks that list used to initialize Array type is not empty.
        Null and empty members are allowed to be in the array by default.

        IndicatorArray is configured to not accept null members, so an error is expected due to
        None or null members being in the input.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicators: custom_indicator_array(allow_null_members=False)

        config_data = {'my_indicators': indicators}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValueError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # error due to None being in input
        assert 'None' in err_msg
        assert 'may not be null' in err_msg

    @pytest.mark.parametrize(
        'types',
        [
            # contains group
            ['Adversary'],
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
    def test_field_type_group_array_custom_entity_filters_invalid(
        self, playbook_app: 'MockApp', types
    ):
        """Test the entity_filter_types customization option of custom_indicator_array.

        The parameter should not allow anything that is not a list of valid indicator types.
        """
        # ensure session singleton is loaded
        app = playbook_app(config_data={})
        tcex = app.tcex
        _ = tcex.inputs.session

        # should raise exception on custom group array config
        with pytest.raises(ConfigurationException):
            custom_indicator_array(entity_filter_types=types)

    @pytest.mark.parametrize('types', [['Host'], ['Address'], ['Host', 'Address']])
    def test_field_type_indicator_array_custom_entity_filters_valid(
        self, playbook_app: 'MockApp', types
    ):
        """Test the entity_filter_types customization option of custom_indicator_array.

        The parameter should not allow anything that is not a list of valid indicator types.
        """
        indicators = [
            {'type': 'Host', 'value': 'domain.com', 'id': '1000'},
            {'type': 'Address', 'value': '1.1.1.1', 'id': '1000'},
        ]

        config_data = {'my_indicators': indicators}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # ensure session singleton is loaded
        _ = tcex.inputs.session

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicators: custom_indicator_array(entity_filter_types=types)

        tcex.inputs.add_model(PytestModel)
        entities = list(tcex.inputs.data.my_indicators.entities())

        # should only contain entities with type that is in configured filter types
        assert all([entity['type'] in types for entity in entities])

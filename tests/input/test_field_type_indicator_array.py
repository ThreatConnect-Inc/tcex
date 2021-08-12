"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import IndicatorArray, IndicatorArrayOptional

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

    def test_field_type_indicator_array_input_invalid(self, playbook_app: 'MockApp'):
        """Test IndicatorArray field type with input that is neither String or TCEntity

        Exception expected, as values are not valid string or TCEntity values
        (multiple variants tested).
        This test validates both the passing of single invalid values and arrays of
        invalid values.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        # binary is not a valid indicator type (not String and not TCEntity)
        invalid_indicator = b'not valid indicator'
        # has no value key
        invalid_indicator2 = {'type': 'Address', 'id': '100'}
        # has no type key
        invalid_indicator3 = {'value': '8.8.8.8', 'id': '100'}
        # type is empty string
        invalid_indicator4 = {'type': '', 'value': '8.8.8.8', 'id': '100'}
        # type is None
        invalid_indicator5 = {'type': None, 'value': '8.8.8.8', 'id': '100'}
        # type is not one of the valid indicator types
        invalid_indicator6 = {'type': 'Adversary', 'value': 'Adversary Name', 'id': '100'}
        # type is anything else
        invalid_indicator7 = {'type': [], 'value': '8.8.8.8', 'id': '100'}
        # missing id
        invalid_indicator8 = {'type': 'Address', 'value': '8.8.8.8'}
        # id is blank
        invalid_indicator9 = {'type': 'Address', 'value': '8.8.8.8', 'id': ''}
        # id is None
        invalid_indicator10 = {'type': 'Address', 'value': '8.8.8.8', 'id': None}
        # value must be a string
        invalid_indicator11 = {'type': [], 'value': [], 'id': '100'}

        # same scenarios as above, except using array inputs
        invalid_indicator12 = [b'not valid indicator']
        # has no value key
        invalid_indicator13 = [{'type': 'Address', 'id': '100'}]
        # has no type key
        invalid_indicator14 = [{'value': '8.8.8.8', 'id': '100'}]
        # type is empty string
        invalid_indicator15 = [{'type': '', 'value': '8.8.8.8', 'id': '100'}]
        # type is None
        invalid_indicator16 = [{'type': None, 'value': '8.8.8.8', 'id': '100'}]
        # type is not one of the valid indicator types
        invalid_indicator17 = [{'type': 'Adversary', 'value': 'Adversary Name', 'id': '100'}]
        # type is anything else
        invalid_indicator18 = [{'type': [], 'value': '8.8.8.8', 'id': '100'}]
        # missing id
        invalid_indicator19 = [{'type': 'Address', 'value': '8.8.8.8'}]
        # id is blank
        invalid_indicator20 = [{'type': 'Address', 'value': '8.8.8.8', 'id': ''}]
        # id is None
        invalid_indicator21 = [{'type': 'Address', 'value': '8.8.8.8', 'id': None}]
        # value must be a string
        invalid_indicator22 = [{'type': [], 'value': [], 'id': '100'}]

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_indicator: IndicatorArray
            my_indicator2: IndicatorArray
            my_indicator3: IndicatorArray
            my_indicator4: IndicatorArray
            my_indicator5: IndicatorArray
            my_indicator6: IndicatorArray
            my_indicator7: IndicatorArray
            my_indicator8: IndicatorArray
            my_indicator9: IndicatorArray
            my_indicator10: IndicatorArray
            my_indicator11: IndicatorArray
            my_indicator12: IndicatorArray
            my_indicator13: IndicatorArray
            my_indicator14: IndicatorArray
            my_indicator15: IndicatorArray
            my_indicator16: IndicatorArray
            my_indicator17: IndicatorArray
            my_indicator18: IndicatorArray
            my_indicator19: IndicatorArray
            my_indicator20: IndicatorArray
            my_indicator21: IndicatorArray
            my_indicator22: IndicatorArray

        config_data = {
            'my_indicator': '#App:1234:my_indicator!Binary',
            'my_indicator2': invalid_indicator2,
            'my_indicator3': invalid_indicator3,
            'my_indicator4': invalid_indicator4,
            'my_indicator5': invalid_indicator5,
            'my_indicator6': invalid_indicator6,
            'my_indicator7': invalid_indicator7,
            'my_indicator8': invalid_indicator8,
            'my_indicator9': invalid_indicator9,
            'my_indicator10': invalid_indicator10,
            'my_indicator11': invalid_indicator11,
            'my_indicator12': '#App:1234:my_indicator12!Binary',
            'my_indicator13': invalid_indicator13,
            'my_indicator14': invalid_indicator14,
            'my_indicator15': invalid_indicator15,
            'my_indicator16': invalid_indicator16,
            'my_indicator17': invalid_indicator17,
            'my_indicator18': invalid_indicator18,
            'my_indicator19': invalid_indicator19,
            'my_indicator20': invalid_indicator20,
            'my_indicator21': invalid_indicator21,
            'my_indicator22': invalid_indicator22,
        }
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        # must stage binary values
        self._stage_key_value(
            'my_indicator', '#App:1234:my_indicator!Binary', invalid_indicator, tcex
        )
        self._stage_key_value(
            'my_indicator12', '#App:1234:my_indicator12!BinaryArray', invalid_indicator12, tcex
        )

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)

        # all IndicatorArray definitions in model resulted in error
        assert all(entity in err_msg for entity in config_data.keys())

        # all IndicatorArray definitions resulted in the same error
        assert err_msg.count("not of Array's type") == len(config_data.keys())

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

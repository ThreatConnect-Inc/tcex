"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import StringArray, StringArrayOptional

from .input_test import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeStringArray(InputTest):
    """Test TcEx StringArray and StringArrayOptional Inputs"""

    def test_field_type_string_array_input_string_string_staged(self, playbook_app: 'MockApp'):
        """Test StringArray field type with string input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', 'string', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['string']

    def test_field_type_string_array_input_string_array_staged(self, playbook_app: 'MockApp'):
        """Test StringArray field type with string array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': '#App:1234:my_string!StringArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!StringArray', ['string'], tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['string']

    def test_field_type_string_array_input_object(self, playbook_app: 'MockApp'):
        """Test StringArray field type with string input.

        Exception expected, as value is not a string value

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': {}}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert 'Value "{}"' in err_msg and "not of Array's type" in err_msg

    def test_field_type_string_array_input_non_string_array(self, playbook_app: 'MockApp'):
        """Test StringArray field type with array that contains non-string member.

        Exception expected, as value is not a string array

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': [{}]}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert 'Value "{}"' in err_msg and "not of Array's type" in err_msg

    @staticmethod
    def test_field_type_string_array_input_empty(playbook_app: 'MockApp'):
        """Test StringArray field type with empty input.

        This test is expected to fail, as StringArrayOptional type is not used when
        defining my_string.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArray]

        config_data = {'my_string': []}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Array must have at least one element' in str(exc_info.value)

    @staticmethod
    def test_field_type_string_array_optional_input_empty_array(playbook_app: 'MockApp'):
        """Test StringArray field type with empty input.

        No Exception is expected, as StringArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArrayOptional]

        config_data = {'my_string': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == []

    def test_field_type_string_array_input_empty_string(self, playbook_app: 'MockApp'):
        """Test StringArray field type with empty input.

        Exception expected, as value is empty and StringArrayOptional type is not used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArray]

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', '', tcex)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Value "" may not be empty' in str(exc_info.value)

    def test_field_type_string_array_optional_input_empty_string(self, playbook_app: 'MockApp'):
        """Test StringArray field type with empty input.

        No Exception is expected, as StringArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArrayOptional]

        config_data = {'my_string': '#App:1234:my_string!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_string', '#App:1234:my_string!String', '', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string == ['']

    @staticmethod
    def test_field_type_string_array_input_null(playbook_app: 'MockApp'):
        """Test StringArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArray

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_string_array_optional_input_null(playbook_app: 'MockApp'):
        """Test StringArray field type with null input.

        Note: this setup is useful in the scenario where an empty '' is allowed, but we
        want to guarantee that the value will not be None.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: StringArrayOptional

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_optional_field_type_string_array(playbook_app: 'MockApp'):
        """Test StringArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of StringArray with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArray]

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string is None

    @staticmethod
    def test_optional_field_type_string_array_optional(playbook_app: 'MockApp'):
        """Test StringArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of StringArrayOptional with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_string: Optional[StringArrayOptional]

        config_data = {'my_string': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_string is None

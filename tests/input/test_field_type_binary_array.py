"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import BinaryArray, BinaryArrayOptional

from .utils import InputTest

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeBinaryArray(InputTest):
    """Test TcEx BinaryArray and BinaryArrayOptional Inputs"""

    def test_field_type_binary_array_input_binary_string_staged(self, playbook_app: 'MockApp'):
        """Test BinaryArray field type with binary input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': '#App:1234:my_binary!Binary'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_binary', '#App:1234:my_binary!Binary', b'binary string', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_binary == [b'binary string']

    def test_field_type_binary_array_input_binary_array_staged(self, playbook_app: 'MockApp'):
        """Test BinaryArray field type with binary array input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': '#App:1234:my_binary!BinaryArray'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(
            'my_binary', '#App:1234:my_binary!BinaryArray', [b'binary string'], tcex
        )
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_binary == [b'binary string']

    def test_field_type_binary_array_input_invalid(self, playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Exception expected, as value is not a binary value

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': 'regular string'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert 'Value "regular string"' in err_msg and "not of Array's type" in err_msg

    def test_field_type_binary_array_input_invalid_array(self, playbook_app: 'MockApp'):
        """Test BinaryArray field type with array that contains non-binary member.

        Exception expected, as value is not a binary array

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': ['regular string']}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        err_msg = str(exc_info.value)
        assert 'Value "regular string"' in err_msg and "not of Array's type" in err_msg

    @staticmethod
    def test_field_type_binary_array_input_empty_array(playbook_app: 'MockApp'):
        """Test BinaryArray field type with empty array input.

        This test is expected to fail, as BinaryArrayOptional type is not used when
        defining my_binary.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArray]

        config_data = {'my_binary': []}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Array must have at least one element' in str(exc_info.value)

    @staticmethod
    def test_field_type_binary_array_optional_input_empty_array(playbook_app: 'MockApp'):
        """Test BinaryArray field type with empty array input.

        No Exception is expected, as BinaryArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArrayOptional]

        config_data = {'my_binary': []}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_binary == []

    def test_field_type_binary_array_input_empty_binary(self, playbook_app: 'MockApp'):
        """Test BinaryArray field type with empty input.

        Exception expected, as value is empty and BinaryArrayOptional type is not used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArray]

        config_data = {'my_binary': '#App:1234:my_binary!Binary'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_binary', '#App:1234:my_binary!Binary', b'', tcex)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert "Value \"b''\" may not be empty" in str(exc_info.value)

    def test_field_type_binary_array_optional_input_empty_binary(self, playbook_app: 'MockApp'):
        """Test BinaryArray field type with empty input.

        No Exception is expected, as BinaryArrayOptional type is used

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArrayOptional]

        config_data = {'my_binary': '#App:1234:my_binary!Binary'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value('my_binary', '#App:1234:my_binary!Binary', b'', tcex)
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_binary == [b'']

    @staticmethod
    def test_field_type_binary_array_input_null(playbook_app: 'MockApp'):
        """Test BinaryArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_binary_array_optional_input_null(playbook_app: 'MockApp'):
        """Test BinaryArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArrayOptional

        config_data = {'my_binary': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_optional_field_type_binary_array(playbook_app: 'MockApp'):
        """Test BinaryArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of BinaryArray with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArray]

        config_data = {'my_binary': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_binary is None

    @staticmethod
    def test_optional_field_type_binary_array_optional(playbook_app: 'MockApp'):
        """Test BinaryArray field type with optional input.

        This behavior is expected because Pydantic does not run validators on None input.
        None is allowed due to the wrapping of BinaryArrayOptional with Optional[] typing.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArrayOptional]

        config_data = {'my_binary': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_binary is None

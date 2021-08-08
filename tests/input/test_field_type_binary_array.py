"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import BinaryArray

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeBinaryArray:
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_field_type_binary_array_input_string(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': 'Pretend this is Binary'}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_binary, list)

    @staticmethod
    def test_field_type_binary_array_input_array(playbook_app: 'MockApp'):
        """Test BinaryArray field type with array input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': ['Pretend this is Binary']}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert isinstance(tcex.inputs.data.my_binary, list)

    @staticmethod
    def test_field_type_binary_array_input_empty(playbook_app: 'MockApp'):
        """Test BinaryArray field type with empty input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArray]

        config_data = {'my_binary': []}
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    @staticmethod
    def test_field_type_binary_array_input_null_required(playbook_app: 'MockApp'):
        """Test BinaryArray field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: BinaryArray

        config_data = {'my_binary': None}
        tcex = playbook_app(config_data=config_data).tcex
        try:
            tcex.inputs.add_model(PytestModel)
            assert False  # this should not hit due to the ValidationError
        except ValidationError:
            assert True  # test should fail on empty ([]) array

    @staticmethod
    def test_field_type_binary_array_optional(playbook_app: 'MockApp'):
        """Test BinaryArray field type with optional input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_binary: Optional[BinaryArray]

        config_data = {'my_binary': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert tcex.inputs.data.my_binary is None
